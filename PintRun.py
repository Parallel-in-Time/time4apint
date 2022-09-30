from PintGraph import PintGraph
from ErrorEstimator import convergenceEstimator
from Task import Task
import sympy as sy
from NameGenerator import NameGenerator


class PintRun:
    def __init__(self, blockIteration, nBlocks, predictor):
        self.blockIteration = blockIteration
        self.predictor = predictor
        self.nBlocks = nBlocks
        self.taskPool = {}
        self.pintGraph = PintGraph()
        self.kMax = convergenceEstimator(nBlocks=self.nBlocks)
        self.null = 0 * sy.symbols('null', commutative=False)
        self.approx_to_computation = {}
        self.computation_to_approx = {}
        self.subtasks = {}
        self.tasks = {}
        self.localsave = {}

        self.taskPool[self.createSymbolForUnk(0, 0)] = Task(op=sy.symbols(f'u_{0}', commutative=False),
                                                            res=self.createSymbolForUnk(0, 0),
                                                            cost=0)

        self.createExpressions()
        self.pintGraph.generateGraphFromPool(pool=self.taskPool)
        self.pintGraph.plotGraph()

    def getMinimalRuntime(self):
        return self.pintGraph.longest_path()

    def createSymbolForUnk(self, n, k):
        if k > self.kMax[n]:
            return sy.symbols(f'u_{n}^{self.kMax[n]}', commutative=False)
        else:
            return sy.symbols(f'u_{n}^{k}', commutative=False)

    def extractTasksFromRule(self, op, res):
        node = op
        tName = NameGenerator(res)
        localTaskPool = {}

        def getTasks(node):
            if node.func in [sy.Add, sy.Mul]:
                name = tName.get()
                # Get operation and dependencies
                if node.func == sy.Add:
                    op = '+'
                elif node.func == sy.Mul:
                    op = 'o'
                ta = [getTasks(n) for n in node.args]
                for i in range(len(ta)):
                    if isinstance(ta[i], sy.Pow):
                        ta[i:i + 1] = [ta[i].base for item in range(ta[i].exp)]
                # Some fix to merge the -1 into one given tasks
                if isinstance(ta[0], sy.core.numbers.NegativeOne):
                    merged = ta[1]
                    ta = [merged] + ta[2:]
                if op == 'o':
                    cou = 1
                    tmp = sy.symbols(name.name + f'_{cou}', commutative=False)
                    while len(ta) > 2:
                        op_tmp = ta[-2:]
                        localTaskPool[tmp] = {'op': op, 'task': ta[-2:]}
                        ta = ta[:-2]
                        ta.append(tmp)
                        cou += 1
                        tmp = sy.symbols(name.name + f'_{cou}', commutative=False)
                # Store task in dictionary
                localTaskPool[name] = {'op': op, 'task': ta}
            else:
                name = node
            return name

        getTasks(node)

        return localTaskPool

    def taskGenerator(self, rule, res):
        localTaskPool = self.extractTasksFromRule(op=rule, res=res)
        for key, value in localTaskPool.items():
            # Rebuild task
            if value['task'][0] in self.localsave:
                value['task'][0] = self.localsave[value['task'][0]]
            expr = value['task'][0]
            for i in range(1, len(value['task'])):
                if value['task'][i] in self.localsave:
                    value['task'][i] = self.localsave[value['task'][i]]
                if value['op'] == 'o':
                    expr *= value['task'][i]
                elif value['op'] == '+':
                    expr += value['task'][i]

            if expr in self.tasks:
                self.localsave[key] = self.tasks[expr]
            else:
                if isinstance(expr, sy.Add) or isinstance(expr, sy.Mul):
                    self.tasks[expr] = key
                    self.taskPool[key] = Task(op=expr, res=key, cost=0)
                else:
                    self.localsave[key] = expr

    def createIterationRule(self, n, k):
        iterationRule = self.null
        if hasattr(self.blockIteration, "NEW_VERSION"):
            for (nMod, kMod), op in self.blockIteration.coeffs:
                iterationRule += op.symbol * self.createSymbolForUnk(
                    n=n + nMod - 1, k=k + kMod - 1)
        else:
            for op in self.blockIteration.getOperators():
                nMod = op.getDepTime()
                kMod = op.getDepIter()
                iterationRule += op.symbol * self.createSymbolForUnk(n=n + nMod, k=k + kMod)
        iterationRule = iterationRule.simplify().expand()
        return iterationRule

    def createPredictionRule(self, n):
        predictorRule = self.null
        if hasattr(self.blockIteration, "NEW_VERSION"):
            for (nMod, _), op in self.blockIteration.predCoeffs:
                predictorRule += op.symbol * self.createSymbolForUnk(
                    n=n + nMod - 1, k=0)
        else:
            for op in self.predictor.getOperators():
                nMod = op.getDepTime()
                predictorRule += op.symbol * self.createSymbolForUnk(n=n + nMod, k=0)
        predictorRule = predictorRule.simplify().expand()
        return predictorRule

    def substitute_and_simplify(self, expr):
        expr = expr.subs(self.approx_to_computation).subs(self.blockIteration.rules)
        return expr.subs(self.computation_to_approx).subs(self.blockIteration.rules)

    def createExpressions(self):

        for n in range(self.nBlocks):
            rule = self.substitute_and_simplify(self.createPredictionRule(n=n + 1))
            res = self.createSymbolForUnk(n=n + 1, k=0)
            self.taskGenerator(rule=rule, res=res)
            self.approx_to_computation[res] = rule
            self.computation_to_approx[rule] = res

        for k in range(max(self.kMax)):
            for n in range(self.nBlocks):
                if k < self.kMax[n + 1]:
                    rule = self.substitute_and_simplify(self.createIterationRule(n=n + 1, k=k + 1))
                    res = self.createSymbolForUnk(n=n + 1, k=k + 1)
                    self.taskGenerator(rule=rule, res=res)
                    self.computation_to_approx[rule] = res
                    self.approx_to_computation[res] = rule

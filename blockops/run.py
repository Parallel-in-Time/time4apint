# Python imports
import re

import sympy as sy

from .error import convergenceEstimator
# BlockOps import
from .graph import PintGraph


class PintRun:
    def __init__(self, blockIteration, nBlocks):
        self.blockIteration = blockIteration
        self.nBlocks = nBlocks
        self.taskPool = {}
        self.kMax = convergenceEstimator(nBlocks=self.nBlocks)
        self.pintGraph = PintGraph(nBlocks, max(self.kMax))
        self.null = 0 * sy.symbols('null', commutative=False)
        self.approx_to_computation = {}
        self.computation_to_approx = {}
        self.equBlockCoeff = {}
        self.subtasks = {}
        self.tasks = {}
        self.localsave = {}

        self.taskPool[self.createSymbolForUnk(0, 0)] = Task(op=self.null,
                                                            result=self.createSymbolForUnk(0, 0),
                                                            cost=0)

        self.createExpressions()
        self.pintGraph.generateGraphFromPool(pool=self.taskPool)
        self.pintGraph.plotGraph()

    def getMinimalRuntime(self):
        return self.pintGraph.longestPath()

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
                    self.taskPool[key] = Task(op=expr, result=key, cost=0)
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
        expr = expr.subs(self.computation_to_approx).subs(self.blockIteration.rules)
        return expr.subs(self.equBlockCoeff).subs(self.blockIteration.rules)

    def createExpressions(self):

        for n in range(self.nBlocks):
            if len(self.blockIteration.predCoeffs) == 0:
                self.taskPool[self.createSymbolForUnk(n + 1, 0)] = Task(op=self.null,
                                                                        result=self.createSymbolForUnk(n + 1, 0),
                                                                        cost=0)
            else:
                rule = self.substitute_and_simplify(self.createPredictionRule(n=n + 1))
                res = self.createSymbolForUnk(n=n + 1, k=0)
                self.taskGenerator(rule=rule, res=res)
                if len(rule.args) > 0:
                    self.approx_to_computation[res] = rule
                    self.computation_to_approx[rule] = res
                else:
                    self.equBlockCoeff[res] = rule

        for k in range(max(self.kMax)):
            for n in range(self.nBlocks):
                if k < self.kMax[n + 1]:
                    rule = self.substitute_and_simplify(self.createIterationRule(n=n + 1, k=k + 1))
                    res = self.createSymbolForUnk(n=n + 1, k=k + 1)
                    self.taskGenerator(rule=rule, res=res)
                    if len(rule.args) > 0:
                        self.computation_to_approx[rule] = res
                        self.approx_to_computation[res] = rule
                    else:
                        self.equBlockCoeff[res] = rule


class NameGenerator(object):
    """DOCTODO"""

    def __init__(self, prefix):
        """
        DOCTODO

        Parameters
        ----------
        prefix : TYPE
            DESCRIPTION.
        """
        self.prefix = prefix
        self.counter = 0

    def get(self):
        if self.counter > 0:
            name = sy.symbols(f'{self.prefix}_{self.counter}', commutative=False)
        else:
            name = sy.symbols(f'{self.prefix}', commutative=False)
        self.counter += 1
        return name


class Task(object):
    """Represents one task"""

    def __init__(self, op, result, cost):
        """
        Creates a task based.

        Parameters
        ----------
        op : TYPE
            DESCRIPTION. Represents the expression that the task performs.
        result : TYPE
            DESCRIPTION. A representation for the result of the expression
        cost : TYPE
            DESCRIPTION. The cost of the task
        """
        self.op = op  # Operation (sympy expression)
        self.result = result  # Result (what is computed by this task)
        self.dep = self.find_dependencies()  # Find dependencies based on op
        # Set a name (only for visualization)
        # TODO: Find a better way to set the name
        if len(op.args) > 0:
            if isinstance(op.args[0], sy.Symbol):
                if len(re.split('u_|u\^', op.args[0].name)) > 1:
                    self.name = result
                else:
                    self.name = op.args[0]
            elif isinstance(op.args[0], sy.Integer):
                func = op.func
                if op.func.is_Mul:
                    func = '*'
                elif op.func.is_Add:
                    func = '+'
                else:
                    raise Exception(f'Unknown func in {self.result}={self.op} with {type(op.func)}')
                self.name = f'{op.args[0]}{func}'
            else:
                raise Exception(f'Unknown operation in {self.result}={self.op} with {type(self.op.args[0])}')
        else:
            self.name = result.name
        self.cost = cost

    def find_dependencies(self):
        """
        Gets the dependencies from the operation (expects dependencies to start with u)

        :return: dependencies
        """
        return [item for item in self.op.atoms() if (isinstance(item, sy.Symbol) and item.name.startswith('u'))]

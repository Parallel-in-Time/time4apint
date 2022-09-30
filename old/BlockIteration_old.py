import sympy as sy
from ModuleBlockOperators import BlockOperators
from ModulePintGraph import PintGraph
from ModuleErrorEstimator import convergenceEstimator


class Task(object):
    def __init__(self, op, res):
        self.op = op  # Operation (sympy expression)
        self.res = res  # Result (what is computed by this task)
        self.dep = self.find_dependencies()  # Find dependencies based on op
        # Set a name (only for visualization)
        if len(op.args) > 0:
            self.name = op.args[0]
        else:
            self.name = 'unknown'
        self.cost = 1  # TODO Make this depend on the task

    def find_dependencies(self):
        """
        Gets the dependencies from the operation (expects dependencies to start with u)

        :return: dependencies
        """
        return [item for item in self.op.atoms() if (isinstance(item, sy.Symbol) and item.name.startswith('u'))]


class NameGenerator(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.counter = 0

    def get(self):
        if self.counter > 0:
            name = sy.symbols(f'{self.prefix}_{self.counter}', commutative=False)
        else:
            name = sy.symbols(f'{self.prefix}', commutative=False)
        self.counter += 1
        return name


class BlockIteration():

    def __init__(self):
        self.taskPool = {}
        self.null = 0 * sy.symbols('null', commutative=False)
        self.nBlock = 3  # TODO: Do we want to optimize this internally? Or is this a parameter?

        # Block operator should be an independent module
        self.blockOp = BlockOperators(variant='parareal')
        self.blockOperators = self.blockOp.getBlockOperator()
        self.f, self.g, self.r, self.p = sy.symbols('f,g, r,p', commutative=False)  # TODO: Get this from the module

        # The convergence estimator should be an independent module
        self.kMax = convergenceEstimator(nBlocks=self.nBlock)

        # Graph module
        self.pintGraph = PintGraph()

        # Run algorithm
        # The algo frame is the same for each algorithm variant. The block operator module should define the variation
        self.algo()

        self.pintGraph.generateGraphFromPool(pool=self.taskPool)
        # self.pintGraph.simplify_graph()
        self.pintGraph.plotGraph()
        self.pintGraph.computeOptimalSchedule(plot=True)

    def node(self, n, k):
        if k > self.kMax[n]:
            return sy.symbols(f'u_{n}^{self.kMax[n]}', commutative=False)
        else:
            return sy.symbols(f'u_{n}^{k}', commutative=False)

    def extractTasks(self, op, res):
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

    def taskGenerator(self, op, res):
        localTaskPool = self.extractTasks(op=op, res=res)
        for key, value in localTaskPool.items():
            # Rebuild task
            expr = value['task'][0]
            for i in range(1, len(value['task'])):
                if value['op'] == 'o':
                    expr *= value['task'][i]
                elif value['op'] == '+':
                    expr += value['task'][i]
            self.taskPool[key] = Task(op=expr, res=key)

    def buildNextNode(self, n, k):
        if k < self.kMax[n + 1]:
            newSol = self.null
            for op in self.blockOperators:
                nMod, kMod = op['dep']
                newSol += op['sym'] * self.node(n + 1 + nMod, k + 1 + kMod)
            newSol.simplify()
            res = self.node(n + 1, k + 1)
            self.taskGenerator(op=newSol, res=res)

    def algo(self):
        self.taskPool[self.node(0, 0)] = Task(op=sy.symbols(f'u_{0}', commutative=False), res=self.node(0, 0))
        for n in range(self.nBlock):
            self.taskPool[self.node(n + 1, 0)] = Task(op=self.g * self.node(n, 0), res=self.node(n + 1, 0))
        for k in range(max(self.kMax)):
            for n in range(self.nBlock):
                self.buildNextNode(n, k)


if __name__ == '__main__':
    BlockIteration()

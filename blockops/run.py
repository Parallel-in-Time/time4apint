# Python imports
import re

import sympy as sy

from .error import convergenceEstimator
# BlockOps import
from .graph import PintGraph
from .taskpool import TaskPool


class PintRun:
    def __init__(self, blockIteration, nBlocks, kMax):
        self.blockIteration = blockIteration
        self.nBlocks = nBlocks
        self.taskPool = TaskPool()
        self.kMax = kMax
        self.pintGraph = PintGraph(nBlocks, max(self.kMax))
        self.null = 0 * sy.symbols('null', commutative=False)
        self.approxToComputation = {}
        self.computationToApprox = {}
        self.equBlockCoeff = {}
        self.subtasks = {}
        self.tasks = {}
        self.localsave = {}

        self.taskPool.addTask(operation=self.null,
                              result=self.createSymbolForUnk(0, 0),
                              cost=0)

        self.createExpressions()
        self.pintGraph.generateGraphFromPool(pool=self.taskPool)

    def getMinimalRuntime(self):
        return self.pintGraph.longestPath()

    def plotGraph(self, figName=None):
        return self.pintGraph.plotGraph(figName)

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
                # Eventually expand [.., op**n, ..] into [.., op, .., op, ..]
                # ONLY for n > 0 !
                for i, sym in enumerate(ta):
                    if isinstance(sym, sy.Pow) and sym.exp > 0:
                        ta[i:i + 1] = [sym.base for item in range(sym.exp)]
                # Some fix to merge the -1 into one given tasks
                if isinstance(ta[0], sy.core.numbers.NegativeOne):
                    merged = ta[1]
                    ta = [merged] + ta[2:]
                if op == 'o':
                    cou = 1
                    tmp = sy.symbols(name.name + f'_{cou}', commutative=False)
                    while len(ta) > 2:
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
                    cost = 0
                    for atoms in expr.atoms():
                        if hasattr(atoms, "name") and atoms.name in self.blockIteration.blockOps:
                            cost = self.blockIteration.blockOps[atoms.name].cost
                    self.taskPool.addTask(operation=expr, result=key, cost=cost)
                else:
                    self.localsave[key] = expr

    def createIterationRule(self, n, k):
        iterationRule = self.null
        for (nMod, kMod), op in self.blockIteration.coeffs:
            iterationRule += op.symbol * self.createSymbolForUnk(
                n=n + nMod - 1, k=k + kMod - 1)
        iterationRule = iterationRule.simplify().expand()
        return iterationRule

    def createPredictionRule(self, n):
        pred = self.blockIteration.predictor
        predictorRule = pred.symbol * self.createSymbolForUnk(n=n - 1, k=0)
        predictorRule = predictorRule.simplify().expand()
        return predictorRule

    def substitute_and_simplify(self, expr):
        expr = expr.subs(self.approxToComputation).subs(self.blockIteration.rules)
        expr = expr.subs(self.computationToApprox).subs(self.blockIteration.rules)
        return expr.subs(self.equBlockCoeff).subs(self.blockIteration.rules)

    def createExpressions(self):

        for n in range(self.nBlocks):
            if self.blockIteration.predictor is None:
                self.taskPool.addTask(operation=self.null,
                                      result=self.createSymbolForUnk(n + 1, 0),
                                      cost=0)
            else:
                rule = self.substitute_and_simplify(self.createPredictionRule(n=n + 1))
                res = self.createSymbolForUnk(n=n + 1, k=0)
                self.taskGenerator(rule=rule, res=res)
                if len(rule.args) > 0:
                    self.approxToComputation[res] = rule
                    self.computationToApprox[rule] = res
                else:
                    self.equBlockCoeff[res] = rule

        for k in range(max(self.kMax)):
            for n in range(self.nBlocks):
                if k < self.kMax[n + 1]:
                    rule = self.substitute_and_simplify(self.createIterationRule(n=n + 1, k=k + 1))
                    res = self.createSymbolForUnk(n=n + 1, k=k + 1)
                    self.taskGenerator(rule=rule, res=res)
                    if len(rule.args) > 0:
                        self.computationToApprox[rule] = res
                        self.approxToComputation[res] = rule
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

# Python imports
import copy
import re

import sympy as sy

# BlockOps import
from .graph import PintGraph
from .taskPool import TaskPool
from .utils import Generator, getFactorizedRule


class PintRun:
    def __init__(self, blockIteration, nBlocks, kMax):
        self.blockIteration = blockIteration
        self.nBlocks = nBlocks
        self.taskPool = TaskPool()
        self.kMax = kMax
        self.pintGraph = PintGraph(nBlocks, max(self.kMax))
        self.approxToComputation = {}
        self.computationToApprox = {}
        self.equBlockCoeff = {}
        self.subtasks = {}
        self.tasks = {}
        self.localsave = {}
        self.generator = [Generator(i) for i in range(max(kMax) + 1)]

        self.taskPool.addTask(ope=sy.core.numbers.Zero(),
                              inp=sy.core.numbers.Zero(),
                              dep=None,
                              n=0,
                              k=0,
                              result=self.createSymbolForUnk(0, 0),
                              blockIters=self.blockIteration.blockOps
                              )

        self.createExpressions()
        self.taskPool.removeTasksRepresentingOne()
        self.pintGraph.generateGraphFromPool(pool=self.taskPool)

    def getMinimalRuntime(self):
        return self.pintGraph.longestPath()

    def plotGraph(self, figName=None, figSize: tuple = (6.4, 4.8), saveFig: str = ""):
        return self.pintGraph.plotGraph(figName, figSize=figSize, saveFig=saveFig)

    def createSymbolForUnk(self, n, k):
        # TODO: Workaround to make FCF work. But maybe this is not the way to go
        if n < 0:
            n = 0
        if k > self.kMax[n]:
            return sy.symbols(f'u_{n}^{self.kMax[n]}', commutative=False)
        else:
            return sy.symbols(f'u_{n}^{k}', commutative=False)

    def createIterationRule(self, n, k):
        iterationRule = sy.core.numbers.Zero()
        for (nMod, kMod), op in self.blockIteration.coeffs:
            iterationRule += op.symbol * self.createSymbolForUnk(n=n + nMod - 1, k=k + kMod - 1)
        iterationRule = iterationRule.simplify().expand()
        return iterationRule

    def createPredictionRule(self, n):
        pred = self.blockIteration.predictor
        predictorRule = pred.symbol * self.createSymbolForUnk(n=n - 1, k=0)
        predictorRule = predictorRule.simplify().expand()
        return predictorRule

    def substitute_and_simplify(self, expr, iter):
        ruleSimplifaction = len(self.blockIteration.rules) > 0
        expr = expr.subs({key: self.approxToComputation[key] for key in
                          [atoms for atoms in expr.atoms() if str(atoms).startswith('u')] if
                          key in self.approxToComputation})
        if ruleSimplifaction:
            expr = expr.subs(self.blockIteration.rules)

        # The saver way is to use the first if case, where all entries of computationToApprox are used.
        # However, this is also quite expensive. Therefore, we only use this strategy
        # for the first two iterations. For these iterations it is necessary, since everything can go
        # back to the initial condition. Afterwards, we use a reduced version of computationToApprox
        # where we only consider entries that contain an u_x^y present in the expr.
        if iter in [0, 1]:
            for key, value in self.computationToApprox.items():
                expr = expr.subs({key: self.computationToApprox[key]})
        else:
            reducedCompuToApprox = {item2[1]: self.computationToApprox[item2[1]] for item2 in
                                    [[key.atoms(), key] for key, value in self.computationToApprox.items()] if
                                    set(item2[0]).intersection(
                                        set([atoms for atoms in expr.atoms() if str(atoms).startswith('u')]))}
            for key, value in reducedCompuToApprox.items():
                expr = expr.subs({key: value})
        tmp = expr
        if ruleSimplifaction:
            tmp = tmp.subs(self.blockIteration.rules)
        if len(self.equBlockCoeff) > 0:
            expr = tmp.subs(self.equBlockCoeff)
            if tmp != expr:
                expr = expr.subs(self.computationToApprox)
                if ruleSimplifaction:
                    expr = expr.subs(self.blockIteration.rules)
        else:
            expr = tmp
        return expr

    def taskGenerator(self, rule, res, n, k):
        # If rule is just a copy of another task
        if type(rule) == sy.Symbol:
            # Computing only if something copies in block direction
            if re.split('_|\^', rule.name)[1] != re.split('_|\^', res.name)[1]:
                ruleDict = getFactorizedRule(rule=rule)
                self.taskPool.createTasks(dico=ruleDict, n=n, k=k, res=res, blockIters=self.blockIteration.blockOps)
                self.taskPool.save = []
        else:
            ruleDict = getFactorizedRule(rule=rule)
            self.taskPool.createTasks(dico=ruleDict, n=n, k=k, res=res, blockIters=self.blockIteration.blockOps)
            self.taskPool.save = []

    def createExpressions(self):

        # Iterate over all blocks
        for n in range(self.nBlocks):
            # If no prediction is given, create tasks that represent initial guess for block n
            if self.blockIteration.predictor is None:
                self.taskPool.addTask(ope=sy.core.numbers.Zero(),
                                      inp=sy.core.numbers.Zero(),
                                      dep=None,
                                      n=n + 1,
                                      k=0,
                                      result=self.createSymbolForUnk(n + 1, 0),
                                      blockIters=self.blockIteration.blockOps
                                      )
            # If predictor is given:
            else:
                # Create results
                res = self.createSymbolForUnk(n=n + 1, k=0)
                # Create rule for block n

                # If no patterns is detected (mode == 0), substitute
                # all existing rules and simplify as much as possible
                if self.generator[0].mode == 0:
                    # If pattern is not detected
                    rule = self.substitute_and_simplify(self.createPredictionRule(n=n + 1), 0)
                    self.generator[0].check(rule, n + 1)
                # Else create rule based on pattern
                else:
                    rule = self.generator[0].generatingExpr(n=n + 1)
                # Generate tasks from rule
                self.taskGenerator(rule=rule, res=res, n=n + 1, k=0)
                # Save rule and results in dictionaries for next iterations and blocks
                if len(rule.args) > 0:
                    self.approxToComputation[res] = rule
                    self.computationToApprox[rule] = res
                else:
                    self.equBlockCoeff[res] = rule

        # Iterate over iterations and blocks
        for k in range(max(self.kMax)):
            for n in range(self.nBlocks):
                if k < self.kMax[n + 1]:
                    # Create results
                    res = self.createSymbolForUnk(n=n + 1, k=k + 1)
                    # Create rule for block n

                    # If no patterns is detected (mode == 0), substitute
                    # all existing rules and simplify as much as possible
                    if self.generator[k + 1].mode == 0:
                        rule = self.substitute_and_simplify(self.createIterationRule(n=n + 1, k=k + 1), k + 1)
                        self.generator[k + 1].check(rule, n + 1)
                    # Else create rule based on pattern
                    else:
                        rule = self.generator[k + 1].generatingExpr(n=n + 1)
                    # Generate tasks from rule
                    self.taskGenerator(rule=rule, res=res, n=n + 1, k=k + 1)
                    # Save rule and results in dictionaries for next iterations and blocks
                    if len(rule.args) > 0:
                        self.computationToApprox[rule] = res
                        self.approxToComputation[res] = rule
                    else:
                        self.equBlockCoeff[res] = rule

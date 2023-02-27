# Python imports
import copy
import re

import sympy as sy

# BlockOps import
from .graph import PintGraph
from .taskpool import TaskPool
from .taskPool2 import TasksPool


class Generator:
    def __init__(self, k, checks=2):
        self.k = k
        self.mode = 0
        self.his = []
        self.checks = checks
        self.generater = ''
        self.translate = {}

    def check(self, expr, n):
        expr_str = f'{expr}'
        unknowns = list(set(re.findall(re.compile('u_\d+\^\d+'), expr_str)))
        tmpWildcard = {}
        for i in range(len(unknowns)):
            tmp_split = re.split('_|\^', unknowns[i])
            iteration = int(tmp_split[2])
            block = int(tmp_split[1])
            tmp_block = f'n-{n - int(block)}' if n - int(block) != 0 else 'n'
            tmp_iter = f'k-{self.k - iteration}' if self.k - iteration != 0 else f'k'
            tmp_str = f'u_{tmp_block}^{tmp_iter}'
            expr_str = expr_str.replace(unknowns[i], tmp_str)
            tmpWildcard[f'x{i}'] = unknowns[i].replace('^', '\^')
            self.translate[f'x{i}'] = [n - int(block), self.k - iteration]
        self.his.append(expr_str)

        if len(self.his) >= self.checks:
            if len(set(self.his[-self.checks:])) == 1:
                self.mode = 1
                self.generater = expr
                for key, val in tmpWildcard.items():
                    self.generater = self.generater.replace(lambda expr: re.match(val, str(expr)),
                                                            lambda expr: sy.Symbol(key, commutative=False))

    def generatingExpr(self, n):
        tmp = self.generater
        for key, val in self.translate.items():
            tmp = tmp.replace(lambda expr: re.match(key, str(expr)),
                              lambda expr: sy.symbols(f'u_{n - val[0]}^{self.k - val[1]}', commutative=False))
        return tmp


Add = sy.core.add.Add
Mul = sy.core.mul.Mul
Pow = sy.core.power.Pow
Symbol = sy.core.symbol.Symbol


def getLeadingTerm(expr: Mul):
    """Decompose a multiplication into its leading term and the rest"""
    try:
        float(expr.args[0])

        # Leading term is a scalar
        if len(expr.args) == 2:
            # Just multiplication
            leading, rest = expr.args
        else:
            # Minus of several multiplicated terms
            leading = expr.args[1]
            rest = Mul(expr.args[0], *expr.args[2:])
    except TypeError:
        # Leading term is a operator
        leading = expr.args[0]
        rest = Mul(*expr.args[1:])

    # if expr.args[0] != -1:
    #     # Non-negative term
    #     leading = expr.args[0]
    #     rest = Mul(*expr.args[1:])
    # else:
    #     # Negative term with leading -1
    #     if len(expr.args) == 2:
    #         # Just minus one term
    #         leading, rest = expr.args
    #     else:
    #         # Minus of several multiplicated terms
    #         leading = expr.args[1]
    #         rest = Mul(-1, *expr.args[2:])
    return leading, rest


def decomposeAddition(expr, dico: dict):
    """Decompose an addition into a dictionnary with leading terms as key"""
    if type(expr) == sy.Mul:
        term = expr
        leading, rest = getLeadingTerm(term)
        try:
            dico[leading] += rest
        except KeyError:
            dico[leading] = rest
    elif type(expr) == sy.Add:
        for term in expr.args:
            if type(term) == Symbol:
                dico[term] = 1
            elif type(term) == Mul:
                leading, rest = getLeadingTerm(term)
                try:
                    dico[leading] += rest
                except KeyError:
                    dico[leading] = rest
            else:
                raise ValueError('got neither Symbol nor Mul')
    else:
        raise Exception('Unknown expression type')
    return dico


def expandTree(dico: dict):
    """Expand an operation tree stored into a dictionnary"""
    for leading, rest in dico.items():
        if rest == 1 or type(rest) == Symbol:
            continue
        if type(rest) == Mul:
            l, r = getLeadingTerm(rest)
            if type(r) == Symbol:
                dico[leading] = {l: r}
            elif type(rest) == Mul:
                subDico = {l: r}
                expandTree(subDico)
                dico[leading] = subDico
        elif type(rest) == Add:
            subDico = decomposeAddition(rest, {})
            expandTree(subDico)
            dico[leading] = subDico
        else:
            raise ValueError('got neither Add nor Mul')


class PintRun:
    def __init__(self, blockIteration, nBlocks, kMax, optimizeSerialPool=False):
        self.blockIteration = blockIteration
        self.nBlocks = nBlocks
        self.taskPool = TaskPool()
        self.taskPool2 = TasksPool()
        self.kMax = kMax
        self.pintGraph = PintGraph(nBlocks, max(self.kMax))
        self.null = 0 * sy.symbols('null', commutative=False)
        self.approxToComputation = {}
        self.computationToApprox = {}
        self.equBlockCoeff = {}
        self.subtasks = {}
        self.tasks = {}
        self.localsave = {}
        self.generator = [Generator(i) for i in range(max(kMax) + 1)]

        self.taskPool.addTask(operation=self.null,
                              result=self.createSymbolForUnk(0, 0),
                              cost=0)
        self.taskPool2.addTask(ope=self.null,
                               inp=self.null,
                               dep=None,
                               n=0,
                               k=0,
                               result=self.createSymbolForUnk(0, 0),
                               blockIters=self.blockIteration.blockOps
                               )

        self.createExpressions()
        self.taskPool2.removeZeroTasks()
        self.taskPool2.setCosts()
        if optimizeSerialPool:
            self.taskPool.optimizeSerialPool()

        self.pintGraph.generateGraphFromPool(pool=self.taskPool2)

    def getMinimalRuntime(self):
        return self.pintGraph.longestPath()

    def plotGraph(self, figName=None, figSize=(6.4, 4.8)):
        return self.pintGraph.plotGraph2(figName, figSize=figSize)
        #return self.pintGraph.plotGraph(figName, figSize=figSize)

    def createSymbolForUnk(self, n, k):
        # TODO: Workaround to make FCF work. But maybe this is not the way to go
        if n < 0:
            n = 0
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

    def taskGenerator2(self, rule, res, n, k):
        dico = decomposeAddition(rule, {})
        expandTree(dico)
        print('Factorized dictionnary :')
        print(' -- note : (+) are additions, (x) are multiplications')

        # Helping function for printing
        def printFacto(dico: dict, tab=0):
            indent = " " * 3 * tab + "(+)"
            for key, val in dico.items():
                if type(val) == dict:
                    print(f'{indent} {key} (x)')
                    printFacto(val, tab + 1)
                else:
                    print(f'{indent} {key} (x) {val}')

        printFacto(dico)
        self.taskPool2.createTasks(dico=dico, n=n, k=k, res=res, blockIters = self.blockIteration.blockOps)
        self.taskPool2.save=[]
        #print('List of tasks :')

        # a = self.taskPool2.pool.pop(res)
        # self.taskPool2.pool[res] = a
    def createExpressions(self):

        for n in range(self.nBlocks):
            if self.blockIteration.predictor is None:
                self.taskPool.addTask(operation=self.null,
                                      result=self.createSymbolForUnk(n + 1, 0),
                                      cost=0)
            else:
                res = self.createSymbolForUnk(n=n + 1, k=0)
                if self.generator[0].mode == 0:
                    rule = self.substitute_and_simplify(self.createPredictionRule(n=n + 1), 0)
                    self.generator[0].check(rule, n + 1)
                else:
                    rule = self.generator[0].generatingExpr(n=n + 1)
                self.taskGenerator(rule=rule, res=res)
                self.taskGenerator2(rule=rule, res=res, n=n+1, k=0)
                if len(rule.args) > 0:
                    self.approxToComputation[res] = rule
                    self.computationToApprox[rule] = res
                else:
                    self.equBlockCoeff[res] = rule

        for k in range(max(self.kMax)):
            for n in range(self.nBlocks):
                if k < self.kMax[n + 1]:
                    res = self.createSymbolForUnk(n=n + 1, k=k + 1)
                    tmp = self.createIterationRule(n=n + 1, k=k + 1)
                    if self.generator[k + 1].mode == 0:
                        rule = self.substitute_and_simplify(self.createIterationRule(n=n + 1, k=k + 1), k + 1)
                        self.generator[k + 1].check(rule, n + 1)
                    else:
                        rule = self.generator[k + 1].generatingExpr(n=n + 1)
                    self.taskGenerator(rule=rule, res=res)
                    self.taskGenerator2(rule=rule, res=res, n=n+1, k=k+1)
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

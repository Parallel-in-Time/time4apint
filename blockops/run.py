# Python imports
import copy
import re
import sympy as sy

# BlockOps import
from blockops.utils.expr import Generator, getFactorizedRule


class PintRun:
    """
    Class representing a parallel-in-time run for a given
    block iteration, number of blocks and number of iterations
    per block.

    For each block/iteration, a rule is created based on the
    block iteration.
    """

    def __init__(self, blockIteration, nBlocks: int, kMax: list) -> None:
        """
        Constructor to initialize a parallel-in-time run.

        Parameters
        ----------
        blockIteration : BlockIteration
            The block iteration
        nBlocks : int
            Number of blocks
        kMax : list
            Number of iterations per block
        Returns
        -------
        expr : sy.Symbol
            Symbol for u_n_k
        """
        self.blockIteration = blockIteration  # The block iteration
        self.nBlocks = nBlocks  # Number of blocks
        self.kMax = kMax  # Maximum number of iterations per block
        self.approxToComputation = {}  # Dictionary result to rule for simplifications
        self.computationToApprox = {}  # Dictionary rule to result for simplifications
        self.equBlockCoeff = {}  # Dictionary for simplifications of equivalent block coefficients
        self.generator = [Generator(i) for i in range(max(kMax) + 1)]  # Rule generator for reduced computation times
        self.blockRules = {}
        self.facBlockRules = {}
        self.exactPropagated = self.createSymbolForUnk(0, 0)
        self.startBlock = 0

        self.blockRules[(0, 0)] = {'result': self.createSymbolForUnk(0, 0),
                                   'rule': sy.core.numbers.Zero() * sy.core.numbers.Zero()}

        self.multiStepRule = {}
        for key, value in self.blockIteration.blockCoeffs.items():
            if key[0] < 0:
                for i in range(key[0], 0, 1):
                    for z in range(max(kMax)):
                        newKey = self.blockIteration.propagator.symbol * self.createSymbolForUnk(n=i, k=z)
                        newValue = self.createSymbolForUnk(n=i + 1, k=z)
                        self.multiStepRule[newKey] = newValue

        # Iterate over all expression
        self.createExpressions()

        self.factorizeBlockRules()

    def createSymbolForUnk(self, n: int, k: int) -> sy.Symbol:
        """
        Create symbol which represent one approximation u_n_k

        Parameters
        ----------
        n : int
            Current block
        k : int
            Current iteration

        Returns
        -------
        expr : sy.Symbol
            Symbol for u_n_k
        """
        if k > self.kMax[n]:
            return sy.symbols(f'u_{n}^{self.kMax[n]}', commutative=False)
        else:
            return sy.symbols(f'u_{n}^{k}', commutative=False)

    def createIterationRule(self, n: int, k: int):
        """
        Create iteration rule for one block and iteration

        Parameters
        ----------
        n : int
            Current block
        k : int
            Current iteration

        Returns
        -------
        expr : sy.Symbol, sy.Mul, sy.Add
            Iteration rule
        """

        iterationRule = sy.core.numbers.Zero()
        for (nMod, kMod), op in self.blockIteration.coeffs:
            iterationRule += op.symbol * self.createSymbolForUnk(n=n + nMod - 1, k=k + kMod - 1)
        iterationRule = iterationRule.simplify().expand()
        return iterationRule

    def createPredictionRule(self, n: int):
        """
        Create prediction rule for one block

        Parameters
        ----------
        n : int
            Current block

        Returns
        -------
        expr : sy.Symbol, sy.Mul, sy.Add
            Predictor rule
        """

        pred = self.blockIteration.predictor
        predictorRule = pred.symbol * self.createSymbolForUnk(n=n - 1, k=0)
        predictorRule = predictorRule.simplify().expand()
        return predictorRule

    def checkForNegativBlocks(self, expr):
        result = re.compile("u_-").search(str(expr))
        if result is None:
            return False
        else:
            return True

    def substituteAndSimplify(self, expr, res, k: int):
        """
        Simplifies expression

        Parameters
        ----------
        expr : sy.Symbol, sy.Mul, sy.Add
            The expression to be simplified
        k : int
            Current iteration

        Returns
        -------
        expr : sy.Symbol, sy.Mul, sy.Add
            Simplified expression
        """

        if len(self.multiStepRule) and self.checkForNegativBlocks(expr):
            expr = expr.subs(self.multiStepRule)

        # Check if rules for the block operation exist
        ruleSimplifaction = len(self.blockIteration.rules) > 0

        # Expand expression based on previous result:rule pairs
        # Consider only pairs which are directly present in the expression to speed up substitution
        expr = expr.subs({key: self.approxToComputation[key] for key in
                          [atoms for atoms in expr.atoms() if str(atoms).startswith('u')] if
                          key in self.approxToComputation})
        # Apply rules if present
        if ruleSimplifaction:
            expr = expr.subs(self.blockIteration.rules)

        # The saver way is to use the first if case, where all entries of computationToApprox are used.
        # However, this is also quite expensive. Therefore, we only use this strategy
        # for the first two iterations. For these iterations it is necessary, since everything can go
        # back to the initial condition. Afterwards, we use a reduced version of computationToApprox
        # where we only consider entries that contain an u_x^y present in the expr.
        # if k in [0, 1,2,3,4,5]:
        if True: # TODO: Make this cheaper again
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
        # Apply rules if present
        if ruleSimplifaction:
            tmp = tmp.subs(self.blockIteration.rules)

        # Simplify if equivalent block iterations exists (in terms of u_x_y = u_z_k)
        if len(self.equBlockCoeff) > 0:
            expr = tmp.subs(self.equBlockCoeff)
            if tmp != expr:
                expr = expr.subs(self.computationToApprox)
                # Apply rules if present
                if ruleSimplifaction:
                    expr = expr.subs(self.blockIteration.rules)
        else:
            expr = tmp

        # If the block iteration of this block contains the exact propagation
        # from an exact state, only this propagation is used and all other
        # computation of the block are discared. Further, the last exact state
        # and the latest exact block index is updated.
        if str(self.blockIteration.propagator.symbol * self.exactPropagated) in str(expr):
            expr = self.blockIteration.propagator.symbol * self.exactPropagated
            self.exactPropagated = res
            self.startBlock = int(str(res).replace('^', '_').split('_')[1])

        return expr

    def createExpressions(self):
        """
        Creates all rules and result for a given block iteration
        """

        # Iterate over all blocks
        for n in range(self.nBlocks):
            if n >= self.startBlock:
                # If no prediction is given, set rule to zero
                if self.blockIteration.predictor is None:
                    self.blockRules[(n + 1, 0)] = {'result': self.createSymbolForUnk(n + 1, 0),
                                                   'rule': sy.core.numbers.Zero()}
                # If predictor is given:
                else:
                    # Create results
                    res = self.createSymbolForUnk(n=n + 1, k=0)
                    # Create rule for block n

                    # If no patterns is detected (mode == 0), substitute
                    # all existing rules and simplify as much as possible
                    if self.generator[0].mode == 0:
                        # If pattern is not detected
                        rule = self.substituteAndSimplify(self.createPredictionRule(n=n + 1), res, 0)
                        self.generator[0].check(rule, n + 1)
                    # Else create rule based on pattern
                    else:
                        rule = self.generator[0].generatingExpr(n=n + 1)
                    # Save rule and results in dictionaries for next iterations and blocks
                    if len(rule.args) > 0:
                        self.approxToComputation[res] = rule
                        self.computationToApprox[rule] = res
                    else:
                        self.equBlockCoeff[res] = rule
                    self.blockRules[(n + 1, 0)] = {'result': res, 'rule': rule}

        # Iterate over iterations and blocks
        for k in range(max(self.kMax)):
            for n in range(self.nBlocks):
                if n >= self.startBlock:
                    if k < self.kMax[n + 1]:
                        # Create results
                        res = self.createSymbolForUnk(n=n + 1, k=k + 1)
                        # Create rule for block n

                        # If no patterns is detected (mode == 0), substitute
                        # all existing rules and simplify as much as possible
                        if self.generator[k + 1].mode == 0:
                            rule = self.substituteAndSimplify(self.createIterationRule(n=n + 1, k=k + 1), res, k + 1)
                            self.generator[k + 1].check(rule, n + 1)
                        # Else create rule based on pattern
                        else:
                            rule = self.generator[k + 1].generatingExpr(n=n + 1)
                        # Save rule and results in dictionaries for next iterations and blocks
                        if len(rule.args) > 0:
                            self.computationToApprox[rule] = res
                            self.approxToComputation[res] = rule
                        else:
                            self.equBlockCoeff[res] = rule

                        self.blockRules[(n + 1, k + 1)] = {'result': res, 'rule': rule}

    def factorizeBlockRules(self) -> None:
        """
        Factorizes the block rules and saves everything in a dictionary
        """
        for key, value in self.blockRules.items():
            self.facBlockRules[key] = {'rule': self.factorize(rule=value['rule'], res=value['result']),
                                       'result': value['result']
                                       }

    def factorize(self, rule, res: sy.Symbol) -> dict:
        """
        Generates tasks based on a given rule.

        Parameters
        ----------
        rule : sy.Symbol, sy.Mul, sy.Add
            The rule to compute the block iteration for n and k
        res : sy.Symbol
            The name of the result

        Returns
        -------
        ruleDict : dict
            Dictionary representing factorized expression
        """

        # If rule is just a copy of another task
        if type(rule) == sy.Symbol:
            # Computing only if something copies in block direction
            if re.split('_|\^', rule.name)[1] != re.split('_|\^', res.name)[1]:
                ruleDict = getFactorizedRule(rule=rule)
            else:
                ruleDict = None
        elif type(rule) == sy.Add or type(rule) == sy.Mul:
            ruleDict = getFactorizedRule(rule=rule)
        elif type(rule) == sy.core.numbers.Zero:
            ruleDict = sy.core.numbers.Zero()
        else:
            raise Exception(f'Unknown type of rule in task generato: {type(rule)}')
        return ruleDict

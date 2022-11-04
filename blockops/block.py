#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 13:17:29 2022

@author: cpf5546
"""
import sympy as sy
import numpy as np

from .utils import getCoeffsFromFormula

# -----------------------------------------------------------------------------
# Block Operator class & specific operators
# -----------------------------------------------------------------------------
class BlockOperator(object):
    """DOCTODO"""

    # Constructor
    def __init__(self, name, cost=1, matrix=None, invert=False):
        """
        DOCTODO

        Parameters
        ----------
        name : TYPE
            DESCRIPTION.
        cost : TYPE, optional
            DESCRIPTION. The default is 1.
        matrix : TYPE, optional
            DESCRIPTION. The default is None.
        invert : TYPE, optional
            DESCRIPTION. The default is False.
        """
        # Common to everyone
        self.symbol = sy.symbols(name, commutative=False)
        self.matrix = np.array([[1]]) if matrix is None else matrix
        # For mono-component blocks operators
        self.cost = cost
        # For multicomponent blocks operators
        self.components = {self.name: self}
        # If performing an inversion or not
        self.invert = invert

    def copy(self):
        new = BlockOperator('mouahaha',
            cost=self.cost, matrix=self.matrix.copy(), invert=self.invert)
        try:
            new.symbol = self.symbol.copy()
        except (TypeError, AttributeError):
            new.symbol = self.symbol
        new.components = self.components.copy()
        return new

    @property
    def name(self):
        return self.symbol.__str__()

    # -------------------------------------------------------------------------
    # Object representation
    # -------------------------------------------------------------------------
    def __str__(self): return f"{self.name} (BlockOp)"

    def __repr__(self): return self.__str__()

    # -------------------------------------------------------------------------
    # Arithmetic operator overloading
    # -------------------------------------------------------------------------
    def __iadd__(self, other):
        if isinstance(other, BlockOperator):
            self.components.update(other.components)
            self.symbol += other.symbol
            self.matrix += other.matrix
            self.cost = None
        else:
            raise ValueError(
                'incompatible addition between BlockOperator '
                f'and {other.__class__.__name__} ({other})')
        return self

    def __isub__(self, other):
        if isinstance(other, BlockOperator):
            self.components.update(other.components)
            self.symbol -= other.symbol
            self.matrix -= other.matrix
            self.cost = None
        else:
            raise ValueError(
                'incompatible substraction between BlockOperator '
                f'and {other.__class__.__name__} ({other})')
        return self

    def __imul__(self, other):
        if isinstance(other, BlockOperator):
            self.components.update(other.components)
            self.symbol *= other.symbol
            if self.invert:
                if other.invert:
                    self.matrix = np.dot(other.matrix, self.matrix)
                else:
                    self.matrix = np.linalg.solve(self.matrix, other.matrix)
                    self.invert = False
            else:
                if other.invert:
                    raise NotImplementedError()
                else:
                    self.matrix = np.dot(self.matrix, other.matrix)
            self.cost = None
        else:
            raise ValueError(
                'incompatible multiplication between BlockOperator '
                f'and {other.__class__.__name__} ({other})')
        return self

    def __ipow__(self, n):
        if n == -1:
            self.invert ^= True
            self.symbol **= -1
            return self
        else:
            raise ValueError(
                'power operator can only be used to generate the inverse '
                'of a block operator')

    def __neg__(self):
        res = self.copy()
        res.symbol *= -1
        res.matrix *= -1
        return res

    def __pos__(self):
        return self

    def __add__(self, other):
        res = self.copy()
        res += other
        return res

    def __sub__(self, other):
        res = self.copy()
        res += -other
        return res

    def __mul__(self, other):
        res = self.copy()
        res *= other
        return res

    def __pow__(self, n):
        res = self.copy()
        res **= n
        return res

    def __call__(self, u):
        if self.invert:
            return np.linalg.solve(self.matrix, u)
        else:
            return np.dot(self.matrix, u)

# Identity block operator
class BlockIdentity(BlockOperator):
    def __init__(self, M, cost=0):
        super().__init__('I', cost, matrix=np.eye(M))
        self.symbol = 1

one = BlockIdentity(1, cost=0)

# -----------------------------------------------------------------------------
# Block Iteration class
# -----------------------------------------------------------------------------
class BlockIteration(object):
    """DOCTODO"""

    NEW_VERSION = None

    def __init__(self, update, predictor='', rules=None, **blockOps):
        """
        DOCTODO

        Parameters
        ----------
        update : TYPE
            DESCRIPTION.
        predictor : TYPE
            DESCRIPTION.
        rules : TYPE, optional
            DESCRIPTION. The default is None.
        **blockOps : TYPE
            DESCRIPTION.
        """
        # Store block coefficients from the iteration update formula
        self.blockCoeffs = getCoeffsFromFormula(update, blockOps)

        # Store block coefficients from the predictor formula
        self.predBlockCoeffs = getCoeffsFromFormula(predictor, blockOps)

        # Stores the generated symbols for the rules
        # TODO : check if the rules hold with the given matrices
        rules = [] if rules is None else rules
        def condEval(x):
            if isinstance(x, BlockOperator):
                return x.symbol
            else:
                e = eval(x, blockOps)
                if hasattr(e, 'symbol'):
                    return e.symbol
                else:
                    return e
        self.rules = {condEval(a): condEval(b) for a,b in rules}

    @property
    def coeffs(self):
        """Return an iterator on the (key, values) of blockCoeffs"""
        return self.blockCoeffs.items()

    def __call__(self, u0, K, N):
        u0 = np.asarray(u0)
        u = np.zeros((K+1, N+1, u0.size), dtype=u0.dtype)
        u[:, 0] = u0
        # Prediction
        pred = self.predBlockCoeffs[(0, 0)]
        for n in range(N):
            u[0, n+1] = pred(u[0, n])
        # Iterations
        for k in range(K):
            for n in range(N):
                for (nMod, kMod), blockOp in self.coeffs:
                    u[k+1, n+1] += blockOp(u[k+kMod, n+nMod])
        return u[:, 1:]

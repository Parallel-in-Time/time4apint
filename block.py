#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 13:17:29 2022

@author: cpf5546
"""
import sympy as sy
import numpy as np

from utils import extractTerm

# -----------------------------------------------------------------------------
# Block Operator class & specific operators
# -----------------------------------------------------------------------------
class BlockOperator(object):

    # Constructor
    def __init__(self, name, cost=1, matrix=None):
        # Common to everyone
        self.symbol = sy.symbols(name, commutative=False)
        self.matrix = np.array([[1]]) if matrix is None else matrix
        # For mono-component blocks operators
        self.cost = cost
        # For multicomponent blocks operators
        self.components = {self.name: self}

    def copy(self):
        new = BlockOperator('mouahaha', cost=self.cost, matrix=self.matrix)
        try:
            new.symbol = self.symbol.copy()
        except TypeError:
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
        else:
            raise ValueError(
                'Incompatible addition between BlockOperator '
                f'and {other.__class__.__name__} ({other})')
        return self

    def __isub__(self, other):
        if isinstance(other, BlockOperator):
            self.components.update(other.components)
            self.symbol -= other.symbol
            self.matrix -= other.matrix
        else:
            raise ValueError(
                'Incompatible substraction between BlockOperator '
                f'and {other.__class__.__name__} ({other})')
        return self

    def __imul__(self, other):
        if isinstance(other, BlockOperator):
            self.components.update(other.components)
            self.symbol *= other.symbol
            self.matrix = self.matrix @ other.matrix
        else:
            raise ValueError(
                'Incompatible multiplication between BlockOperator '
                f'and {other.__class__.__name__} ({other})')
        return self

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

# Preinstantiated block operators
one = BlockOperator('Id', cost=0)
one.symbol = 1
zero = BlockOperator('O', cost=0)
zero.symbol = 0
zero.matrix *= 0

# -----------------------------------------------------------------------------
# Block Iteration class
# -----------------------------------------------------------------------------
class BlockIteration(object):

    def __init__(self, expr, rules=None, **blockOps):
        blockCoeffs = {}
        while expr != '':
            nIndex, kIndex, block, expr = extractTerm(expr)
            blockCoeffs[(nIndex, kIndex)] = eval(block, blockOps)
        self.blockCoeffs = blockCoeffs

        rules = [] if rules is None else rules
        condEval = lambda x: \
            x if isinstance(x, BlockOperator) \
            else eval(x, blockOps)
        self.rules = [(condEval(a), condEval(b)) for a,b in rules]


# Quick script testing
if __name__ == '__main__':

    g = BlockOperator('g')
    f = BlockOperator('f')
    r = BlockOperator('r')
    p = BlockOperator('p')

    rules = [(r*p, one)]

    parareal = BlockIteration(
        "(f - p*g*r)u_{n}^k + p*g*r*u_{n}^{k+1}", **locals())

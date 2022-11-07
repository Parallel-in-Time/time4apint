#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 13:17:29 2022

@author: cpf5546
"""
import sympy as sy
import numpy as np

# -----------------------------------------------------------------------------
# Block Operator class & specific operators
# -----------------------------------------------------------------------------
class BlockOperator(object):
    """DOCTODO"""

    # Constructor
    def __init__(self, name=None, cost=0, matrix=None, invert=None):
        """
        DOCTODO

        Parameters
        ----------
        name : TYPE, optional
            DESCRIPTION. The default is 'I'.
        cost : TYPE, optional
            DESCRIPTION. The default is 0.
        matrix : TYPE, optional
            DESCRIPTION. The default is None.
        invert : TYPE, optional
            DESCRIPTION. The default is None.
        """
        if name is None:
            self.symbol = 1
        else:
            self.symbol = sy.symbols(name, commutative=False)
        self.matrix = matrix
        self.invert = invert
        # For mono-component blocks operators
        self.cost = cost
        # For multicomponent blocks operators
        self.components = {self.name: self}


    def copy(self):
        new = BlockOperator(
            cost=self.cost,
            matrix=None if self.matrix is None else self.matrix.copy(),
            invert=None if self.invert is None else self.invert.copy())
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
            if self.invert is not None or other.invert is not None:
                raise ValueError(
                    'cannot add block operator with invert part '
                    f'(here {self})')
            if self.matrix is not None and other.matrix is not None:
                self.matrix += other.matrix
            else:
                self.matrix = None
            self.components.update(other.components)
            self.symbol += other.symbol
            self.cost = None
        else:
            raise ValueError(
                'incompatible addition between BlockOperator '
                f'and {other.__class__.__name__} ({other})')
        return self

    def __isub__(self, other):
        if isinstance(other, BlockOperator):
            if self.invert is not None or other.invert is not None:
                raise ValueError(
                    'cannot substract block operator with invert part '
                    f'(here {self})')
            if self.matrix is not None and other.matrix is not None:
                self.matrix -= other.matrix
            else:
                self.matrix = None
            self.components.update(other.components)
            self.symbol -= other.symbol
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
            if self.invert is not None:
                if other.matrix is not None:
                    inv = np.linalg.solve(self.invert, other.matrix)
                    if self.matrix is not None:
                        self.matrix = np.dot(self.matrix, inv)
                    else:
                        self.matrix = inv
                    self.invert = other.invert
                else:
                    if other.invert is not None:
                        self.invert = np.dot(other.invert, self.invert)
            else:
                if self.matrix is None:
                    self.matrix = other.matrix
                elif other.matrix is not None:
                    self.matrix = np.dot(self.matrix, other.matrix)
                self.invert = other.invert
            self.cost = None
        else:
            raise ValueError(
                'incompatible multiplication between BlockOperator '
                f'and {other.__class__.__name__} ({other})')
        return self

    def __ipow__(self, n):
        if n == -1:
            self.invert, self.matrix = self.matrix, self.invert
            self.symbol **= -1
            return self
        else:
            raise ValueError(
                'power operator can only be used to generate the inverse '
                'of a block operator')

    def __neg__(self):
        res = self.copy()
        res.symbol *= -1
        if res.matrix is not None:
            res.matrix *= -1
        elif res.invert is not None:
            res.invert *= -1
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
        if self.invert is not None:
            u = np.linalg.solve(self.invert, u)
        if self.matrix is not None:
            u = np.dot(self.matrix, u)
        return u

# Identity block operator
one = BlockOperator()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 13:17:29 2022

@author: cpf5546
"""
import sympy as sy
import numpy as np

from blockops.utils.vectorize import matVecMul, matVecInv

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

    @property
    def M(self):
        M = 0
        if self.matrix is not None:
            M = self.matrix.shape[-1]
        if self.invert is not None:
            M = max(self.invert.shape[-1], M)
        return M

    @property
    def nLam(self):
        if self.isSymbolic:
            return 0
        nLam = 1
        M = self.M
        if self.matrix is not None:
            nLam = self.matrix.size // (M**2)
        if self.invert is not None:
            nLam = max(self.invert.size // (M**2), nLam)
        return nLam

    @property
    def isSymbolic(self):
        return (self.matrix is None) and (self.invert is None)

    @property
    def isScalar(self):
        try:
            float(self.symbol)
            return self.isSymbolic
        except TypeError:
            return False

    @property
    def isIdentity(self):
        try:
            return self.symbol == self.symbol**(-1)
        except ZeroDivisionError:
            return False

    @property
    def isNull(self):
        return self.symbol + self.symbol == self.symbol

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
            if (self.invert is not None) or (other.invert is not None):
                raise ValueError(
                    'cannot add non symbolic block operator '
                    f'with invert part (here {self})')
            if self.isScalar:
                if not other.isSymbolic:
                    self.matrix = np.eye(other.M, dtype=other.matrix.dtype)
                    self.matrix *= float(self.symbol)
                    try:
                        self.matrix += other.matrix
                    except ValueError:
                        # Different nLam for each block operators
                        self.matrix = self.matrix + other.matrix
            elif not self.isSymbolic:
                if other.isScalar:
                    matrix = np.eye(self.M, dtype=self.matrix.dtype)
                    matrix *= float(other.symbol)
                    self.matrix += matrix
                elif not other.isSymbolic:
                    self.matrix += other.matrix
            self.components.update(other.components)
            self.symbol += other.symbol
            self.cost = max(self.cost, other.cost)
        else:
            raise ValueError(
                'incompatible addition between BlockOperator '
                f'({self}) and {other.__class__.__name__} ({other})')
        return self

    def __isub__(self, other):
        if isinstance(other, BlockOperator):
            if self.invert is not None or other.invert is not None:
                raise ValueError(
                    'cannot substract non symbolic block operator '
                    f'with invert part (here {self})')
            if self.isScalar:
                if not other.isSymbolic:
                    self.matrix = np.eye(other.M, dtype=other.matrix.dtype)
                    self.matrix *= float(self.symbol)
                    try:
                        self.matrix -= other.matrix
                    except ValueError:
                        # Different nLam for each block operators
                        self.matrix = self.matrix - other.matrix
            elif not self.isSymbolic:
                if other.isScalar:
                    matrix = np.eye(self.M, dtype=self.matrix.dtype)
                    matrix *= float(other.symbol)
                    self.matrix -= matrix
                elif not other.isSymbolic:
                    self.matrix -= other.matrix
            self.components.update(other.components)
            self.symbol -= other.symbol
            self.cost = max(self.cost, other.cost)
        else:
            raise ValueError(
                'incompatible substraction between BlockOperator '
                f'({self}) and {other.__class__.__name__} ({other})')
        return self

    def __imul__(self, other):
        if isinstance(other, BlockOperator):
            self.components.update(other.components)
            self.symbol *= other.symbol
            if self.invert is not None:
                if other.matrix is not None:
                    inv = np.linalg.solve(self.invert, other.matrix)
                    if self.matrix is not None:
                        self.matrix = self.matrix @ inv
                    else:
                        self.matrix = inv
                    self.invert = other.invert
                else:
                    if other.invert is not None:
                        self.invert = other.invert @ self.invert
            else:
                if self.matrix is None:
                    self.matrix = other.matrix
                elif other.matrix is not None:
                    self.matrix = self.matrix @ other.matrix
                self.invert = other.invert
            self.cost += other.cost
        elif isinstance(other, (float, int)):
            self.symbol *= other
            if self.matrix is not None:
                self.matrix *= other
            else:
                self.invert *= other
        else:
            raise ValueError(
                'incompatible multiplication between BlockOperator '
                f'({self}) and {other.__class__.__name__} ({other})')
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

    def __rmul__(self, other):
        if isinstance(other, (float, int)):
            return  self.__mul__(other)
        else:
            raise ValueError(
                'incompatible multiplication between BlockOperator '
                f'and {other.__class__.__name__} ({other})')

    def __pow__(self, n):
        res = self.copy()
        res **= n
        return res

    def __call__(self, u):
        if self.invert is not None:
            u = matVecInv(self.invert, u)
        if self.matrix is not None:
            u = matVecMul(self.matrix, u)
        if self.isScalar:
            u = float(self.symbol)*u
        return u

    def __eq__(self, other):
        try:
            return self.symbol == other.symbol
        except AttributeError:
            return self.symbol == other


I = BlockOperator()

def scalarBlock(val):
    op = I.copy()
    op.symbol = val
    return op

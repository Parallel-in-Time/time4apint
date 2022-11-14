#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:15:19 2022

@author: cpf5546
"""
import numpy as np
import pytest

from ..block import BlockOperator

M = 5
m1 = np.random.rand(M, M)
m2 = np.random.rand(M, M)
m3 = np.random.rand(M, M)
m4 = np.random.rand(M, M)
u = np.random.rand(M)

dot = np.dot
solve = np.linalg.solve


class TestBase:

    op = BlockOperator('Op', matrix=m1, invert=m2)

    def testName(self):
        assert self.op.name == 'Op'

    def testEval(self):
        uTest = self.op(u)
        uCheck = dot(m1, solve(m2, u))
        assert np.allclose(uTest, uCheck)

    def testCopy(self):
        op = self.op.copy()
        assert op.name == self.op.name
        assert op.symbol == self.op.symbol
        assert op.components == self.op.components
        assert np.allclose(op(u), self.op(u))

    def testEvalMatrixOnly(self):
        op = self.op.copy()
        op.invert = None
        uTest = op(u)
        uCheck = dot(m1, u)
        assert np.allclose(uTest, uCheck)

    def testEvalInvertOnly(self):
        op = self.op.copy()
        op.matrix = None
        uTest = op(u)
        uCheck = solve(m2, u)
        assert np.allclose(uTest, uCheck)

    def testIdentity(self):
        op = BlockOperator()
        assert op.name == '1'
        assert op.symbol == 1
        assert np.allclose(op(u), u)
        assert op.isIdentity
        assert op.isScalar
        assert op.isSymbolic

class TestArithmetics:

    b1 = BlockOperator('B1', matrix=m1, invert=m2)
    b2 = BlockOperator('B2', matrix=m3, invert=m4)

    def testAddition(self):
        with pytest.raises(ValueError):
            self.b1 + self.b2
        b1 = self.b1.copy()
        b2 = self.b2.copy()
        b1.invert, b2.invert = None, None

        op = b1 + b2
        assert op.name == 'B1 + B2'
        assert op.symbol == b1.symbol + b2.symbol
        assert len(op.components) == 2
        uTest = op(u)
        uCheck = dot(m1, u) + dot(m3, u)
        assert np.allclose(uTest, uCheck)

    def testSubstraction(self):
        with pytest.raises(ValueError):
            self.b1 - self.b2
        b1 = self.b1.copy()
        b2 = self.b2.copy()
        b1.invert, b2.invert = None, None

        op = b1 - b2
        assert op.name == 'B1 - B2'
        assert op.symbol == b1.symbol - b2.symbol
        assert len(op.components) == 2
        uTest = op(u)
        uCheck = dot(m1, u) - dot(m3, u)
        assert np.allclose(uTest, uCheck)

    def testInversion(self):
        op = self.b1**(-1)
        assert op.name == 'B1**(-1)'
        assert op.symbol == self.b1.symbol**(-1)
        assert len(op.components) == 1
        uTest = op(u)
        uCheck = dot(m2, solve(m1, u))
        assert np.allclose(uTest, uCheck)

    def testMultiplication(self):
        op = self.b1 * self.b2
        assert op.name == 'B1*B2'
        assert op.symbol == self.b1.symbol * self.b2.symbol
        assert len(op.components) == 2
        uTest = op(u)
        uCheck = dot(m1, solve(m2,
            dot(m3, solve(m4, u))))
        assert np.allclose(uTest, uCheck)

        op = self.b1 * (self.b1)**(-1)
        assert op.name == '1'
        assert len(op.components) == 1
        uTest = op(u)
        assert np.allclose(uTest, u)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b2.invert = None
        op = b1*b2
        uTest = op(u)
        uCheck = dot(dot(m1, solve(m2, m3)), u)
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b1.invert = None
        op = b1*b2
        uTest = op(u)
        uCheck = dot(dot(m1, m3), solve(m4, u))
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b1.matrix = None
        op = b1*b2
        uTest = op(u)
        uCheck = dot(solve(m2, m3), solve(m4, u))
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b2.matrix = None
        op = b1*b2
        uTest = op(u)
        uCheck = dot(m1, solve(dot(m4, m2), u))
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b1.invert, b2.matrix = None, None
        op = b1*b2
        uTest = op(u)
        uCheck = dot(m1, solve(m4, u))
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b2.invert, b1.matrix = None, None
        op = b1*b2
        uTest = op(u)
        uCheck = dot(solve(m2, m3), u)
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b1.invert, b1.matrix = None, None
        op = b1*b2
        uTest = op(u)
        uCheck = dot(m3, solve(m4, u))
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b2.invert, b2.matrix = None, None
        op = b1*b2
        uTest = op(u)
        uCheck = dot(m1, solve(m2, u))
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b1.invert, b2.invert, b2.matrix = 3*[None]
        op = b1*b2
        uTest = op(u)
        uCheck = dot(m1, u)
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b1.matrix, b2.invert, b2.matrix = 3*[None]
        op = b1*b2
        uTest = op(u)
        uCheck = solve(m2, u)
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b1.matrix, b1.invert, b2.invert = 3*[None]
        op = b1*b2
        uTest = op(u)
        uCheck = dot(m3, u)
        assert np.allclose(uTest, uCheck)

        b1, b2 = self.b1.copy(), self.b2.copy()
        b1.matrix, b1.invert, b2.matrix = 3*[None]
        op = b1*b2
        uTest = op(u)
        uCheck = solve(m4, u)
        assert np.allclose(uTest, uCheck)

        b1, b2 = BlockOperator(), BlockOperator()
        op = b1*b2
        assert np.allclose(op(u), u)

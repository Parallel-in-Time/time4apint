#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:35:00 2022

@author: cpf5546
"""
import numpy as np


def testNumpyOp():
    # Some testing for block operations
    nDOF = 100
    M = 5

    mat = np.random.rand(nDOF, M, M)
    u = np.random.rand(nDOF, M)

    mat = np.squeeze(mat)
    u = np.squeeze(u)

    vecMatMul = np.matmul(mat, u[..., None]).squeeze(axis=-1)
    vecMatInv = np.linalg.solve(mat, u)

    if nDOF == 1:
        assert np.allclose(vecMatMul, mat @ u), 'matMul'
        assert np.allclose(vecMatInv, np.linalg.solve(mat, u)), 'matInv'
    else:
        for i in range(nDOF):
            assert np.allclose(vecMatMul[i], mat[i] @ u[i]), 'matMul'
            assert np.allclose(vecMatInv[i], np.linalg.solve(mat[i], u[i])), 'matInv'

    vecMatMulOne =np.matmul(mat[0], u[..., None]).squeeze(axis=-1)
    vecMatInvOne = np.linalg.solve(mat[0][None, ...], u)

    if nDOF == 1:
        assert np.allclose(vecMatMulOne, mat @ u), 'matMul'
        assert np.allclose(vecMatInvOne, np.linalg.solve(mat, u)), 'matInv'
    else:
        for i in range(nDOF):
            assert np.allclose(vecMatMulOne[i], mat[0] @ u[i]), 'matMul'
            assert np.allclose(vecMatInvOne[i], np.linalg.solve(mat[0], u[i])), 'matInv'

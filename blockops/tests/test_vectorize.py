#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:35:00 2022

@author: tlunet
"""
import numpy as np

M, nDOF = 5, 100

from blockops.vectorize import matVecMul, matVecInv, matMatMul

def generate(M, nDOF):
    mat = np.random.rand(nDOF, M, M)
    u = np.random.rand(nDOF, M)
    mat = np.squeeze(mat)
    u = np.squeeze(u)
    return mat, u


def testMatVecMul():
    """Test vectorized Matrix Vector Multiplication (matVecMul)"""
    mat, u = generate(M, nDOF)

    out = matVecMul(mat, u)

    for i in range(nDOF):
        assert np.allclose(out[i], mat[i] @ u[i])

    out = matVecMul(mat[0], u)

    for i in range(nDOF):
        assert np.allclose(out[i], mat[0] @ u[i])

    out = matVecMul(mat[0], u[0])

    assert np.allclose(out, mat[0] @ u[0])


def testMatVecInv():
    """Test vectorized Matrix Vector Inversion (matVecInv)"""
    mat, u = generate(M, nDOF)

    out = matVecInv(mat, u)

    for i in range(nDOF):
        assert np.allclose(out[i], np.linalg.solve(mat[i], u[i]))

    out = matVecInv(mat[0], u)

    for i in range(nDOF):
        assert np.allclose(out[i], np.linalg.solve(mat[0], u[i]))

    out = matVecInv(mat[0], u[0])

    assert np.allclose(out, np.linalg.solve(mat[0], u[0]))


def testMatMatMul():
    """Test vectorized Matrix Matrix Multiplication (matMatMul)"""
    m1 = generate(M, 1)[0]
    m2 = generate(M, nDOF)[0].transpose((-2, -1, 0))

    out = matMatMul(m1, m2)

    for i in range(nDOF):
        assert np.allclose(out[:, :, i], m1 @ m2[:, :, i])

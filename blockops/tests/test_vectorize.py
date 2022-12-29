#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:35:00 2022

@author: tlunet
"""
import numpy as np

M, nDOF = 5, 100


def generate(M, nDOF):
    mat = np.random.rand(nDOF, M, M)
    u = np.random.rand(nDOF, M)
    mat = np.squeeze(mat)
    u = np.squeeze(u)
    return mat, u

# TODO : put the three following functions in one dedicated module and use them in blockops

def matVecMul(mat, u):
    """Used for blockOps matrix vector multiplication"""
    return np.matmul(mat, u[..., None]).squeeze(axis=-1)


def matVecInv(mat, u):
    """Used for blockOps matrix vector inversion"""
    try:
        return np.linalg.solve(mat, u)
    except ValueError:
        return np.linalg.solve(mat[None, ...], u)


def matMatMul(m1, m2):
    """Used for Z2N / N2N formulation switch"""
    return (m1 @ m2.transpose((1, 0, -1))).transpose((1,0,-1))


def testMatVecMul():
    """Test vectorized Matrix Vector Multiplication (matVecMul):

    - matVecMul((nDOF, M, M), (nDOF, M)) -> (nDOF, M) <=> (M, M) @ (M,) for each nDOF
    - matVecMul((M, M), (nDOF, M)) -> (nDOF, M) <=> (M, M) @ (M,) for each nDOF
    - matVecMul((M, M), (M,)) -> (M,) <=> (M, M) @ (M,)
    """
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
    r"""Test vectorized Matrix Vector Inversion (matVecInv):

    - matVecInv((nDOF, M, M), (nDOF, M)) -> (nDOF, M) <=> (M, M) \ (M,) for each nDOF
    - matVecInv((M, M), (nDOF, M)) -> (nDOF, M) <=> (M, M) \ (M,) for each nDOF
    - matVecInv((M, M), (M,)) -> (M,) <=> (M, M) \ (M,)
    """
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
    """Test vectorized Matrix Matrix Multiplication (matMatMul):

    - matMatMul((M, M), (M, M, nDOF)) -> (M, M, nDOF) <=> (M, M) @ (M, M) for each nDOF
    """
    m1 = generate(M, 1)[0]
    m2 = generate(M, nDOF)[0].transpose((-2, -1, 0))

    out = matMatMul(m1, m2)

    for i in range(nDOF):
        assert np.allclose(out[:, :, i], m1 @ m2[:, :, i])

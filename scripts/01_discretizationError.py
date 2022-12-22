#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:42:11 2022

@author: cpf5546
"""
import numpy as np

from blockops import BlockProblem
from blockops.plots import plotAccuracyContour

reLam = np.linspace(-4, 0.5, 501)
imLam = np.linspace(-3, 3, 500)
N = 1
M = 5
scheme = 'COLLOCATION'

lam = reLam[:, None] + 1j*imLam[None, :]
prob = BlockProblem(
    lam.ravel(), N, N, M, scheme,
    nodes='LEGENDRE', qType='LOBATTO')

uExact = prob.getSolution('exact')
uNum = prob.getSolution('fine')
err = np.abs(uExact-uNum)

stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
errEnd = err[-1, :, -1].reshape(lam.shape)
errMax = np.max(err, axis=(0, -1)).reshape(lam.shape)

err = errMax

# Plot discretization error on complex plane
plotAccuracyContour(reLam, imLam, err, stab)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Display the discretization error for one given problem

Parameters
----------
nBlocks : 
    number of blocks (N)
nPoints : 
    number of time points per block
scheme : 
    type of time scheme used

Other arguments can be given
"""
import numpy as np

from blockops import BlockProblem
from blockops.plots import plotAccuracyContour

reLam = np.linspace(-4, 0.5, 128)
imLam = np.linspace(-3, 3, 128)
nBlocks = 20
nPoints = 5
scheme = 'COLLOCATION'

lam = reLam[:, None] + 1j*imLam[None, :]
prob = BlockProblem(
    lam.ravel(), tEnd=nBlocks, nBlocks=nBlocks, nPoints=nPoints, scheme=scheme,
    points='LEGENDRE', quadType='LOBATTO', collUpdate=False)

uExact = prob.getSolution('exact')
uNum = prob.getSolution('fine')
err = np.abs(uExact-uNum)

stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
errEnd = err[-1, :, -1].reshape(lam.shape)
errMax = np.max(err, axis=(0, -1)).reshape(lam.shape)

err = errMax

# Plot discretization error on complex plane
plotAccuracyContour(reLam, imLam, err, stab)

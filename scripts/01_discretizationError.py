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
import blockops.plots as bp

bp = bp.Plotly


reLam = np.linspace(-4, 0.5, 256)
imLam = np.linspace(-3, 3, 256)
nBlocks = 10

params = {
    "RungeKutta": {
        "rkScheme": 'RK4',
        "nStepsPerPoint": 1,
        "nPoints": 3,
        },
    "Collocation": {
        "nPoints": 4,
        "collUpdate": False}
    }
scheme = "RungeKutta"

lam = reLam[:, None] + 1j*imLam[None, :]
prob = BlockProblem(
    lam.ravel(), tEnd=nBlocks, nBlocks=nBlocks,
    scheme=scheme, **params[scheme])

uExact = prob.getSolution('exact')
uNum = prob.getSolution('fine')
err = np.abs(uExact-uNum)

stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
errEnd = err[-1, :, -1].reshape(lam.shape)
errMax = np.max(err, axis=(0, -1)).reshape(lam.shape)

err = errMax

# Plot discretization error on complex plane
fig = bp.plotAccuracyContour(reLam, imLam, err, stab)
fig.show()

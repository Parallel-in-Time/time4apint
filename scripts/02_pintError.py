#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 09:25:12 2022

@author: tlunet
"""
import numpy as np

from blockops import BlockProblem
from blockops.plots import plotAccuracyContour

zoom = 1
reLam = np.linspace(-4/zoom, 0.5/zoom, 128)
imLam = np.linspace(-3/zoom, 3/zoom, 128)
nBlocks = 10
nPoints = 1
scheme = 'RK4'
nStepsF = 10
nStepsG = 1
algoName = 'Parareal'

lam = reLam[:, None] + 1j*imLam[None, :]
prob = BlockProblem(
    lam.ravel(), tEnd=nBlocks, nBlocks=nBlocks, nPoints=nPoints, 
    scheme='RungeKutta', rkScheme=scheme, nStepsPerPoint=nStepsF)
prob.setApprox('RungeKutta', rkScheme=scheme, nStepsPerPoint=nStepsG)

algo = prob.getBlockIteration(algoName)

uNum = prob.getSolution('fine')
uPar = algo(nIter=4)

err = np.abs(uNum-uPar)

stab = np.abs(uPar)[-1, -1, :, -1].reshape(lam.shape)
errEnd = err[-1, -1, :, -1].reshape(lam.shape)
errMax = np.max(err[-1], axis=(0, -1)).reshape(lam.shape)

err = errMax

# Plot discretization error on complex plane
plotAccuracyContour(reLam, imLam, err, stab)

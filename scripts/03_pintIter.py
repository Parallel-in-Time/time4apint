#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 10:06:40 2022

@author: telu
"""
import numpy as np
import matplotlib.pyplot as plt

from blockops import BlockProblem
from blockops.plots import plotAccuracyContour, plotContour

zoom = 1
reLam = np.linspace(-4 / zoom, 0.5 / zoom, 501)
imLam = np.linspace(-3 / zoom, 3 / zoom, 500)
N = 10
M = 4
schemeF = 'COLLOCATION'
nStepsF = 40
schemeG = 'RK4'
nStepsG = 1
algoName = 'Parareal'

lam = reLam[:, None] + 1j * imLam[None, :]
prob = BlockProblem(
    lam.ravel(), N, N, M, schemeF, nStepsPerPoint=nStepsF,
    points='LEGENDRE', quadType='LOBATTO', form='Z2N')
prob.setApprox(schemeG, nStepsPerPoint=nStepsG)

algo = prob.getBlockIteration(algoName)

# Compute fine solution
uNum = prob.getSolution('fine')

# Compute exact solution and discretization error
uExact = prob.getSolution('exact')
errDiscr = np.abs(uExact - uNum)
errDiscrMax = np.max(errDiscr, axis=(0, -1)).reshape(lam.shape)
stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
plotAccuracyContour(reLam, imLam, errDiscrMax, stab, figName='discrErr')

# Compute approximate solution and error
uApprox = prob.getSolution('approx')
errApprox = np.abs(uNum - uApprox)
errApproxMax = np.max(errApprox, axis=(0, -1)).reshape(lam.shape)
stab = np.abs(uApprox)[0, :, -1].reshape(lam.shape)
plotAccuracyContour(reLam, imLam, errApproxMax, stab, figName='coarseErr')

# Compute PinT solution and error
nIterMax = N
uPar = algo(K=nIterMax)
errPinT = np.abs(uNum - uPar)
errPinTMax = np.max(errPinT, axis=(1, -1)).reshape(
    (errPinT.shape[0],) + (lam.shape))

# Compute required number of iterations to discretization error
nIter = -np.ones_like(errDiscrMax, dtype=int)
nIter *= 2
k = errPinT.shape[0] - 1
for err in errPinTMax[-1::-1]:
    nIter[err < errDiscrMax] = k
    k -= 1

# %% Plotting
plotContour(reLam=reLam, imLam=imLam, val=nIter, nLevels=nIterMax, figName='PinTIter')

#TODO: The following plots give an idea what we might want. But not 100% sure.
if True:
    #Optimal scheduling
    reqIters = np.unique(nIter)
    runtimeOpt = np.zeros(N + 1)
    for k in range(1, N + 1):
        if k in reqIters:
            runtimeOpt[k] = algo.getRuntime(N=N, K=k, nProc=N, schedule_type='OPTIMAL')
    nRuntime = runtimeOpt[nIter]

    # %% Plotting
    plotContour(reLam=reLam, imLam=imLam, val=nRuntime, figName='PinTRuntime Optimal Schedule')

    #Block-by-Block scheduling
    runtimeBbB = np.zeros(N + 1)
    for k in range(1, N + 1):
        if k in reqIters:
            runtimeBbB[k] = algo.getRuntime(N=N, K=k, nProc=N, schedule_type='BLOCK-BY-BLOCK')
    nRuntime = runtimeBbB[nIter]

    # %% Plotting
    plotContour(reLam=reLam, imLam=imLam, val=nRuntime, figName='PinTRuntime Block-by-Block Schedule')


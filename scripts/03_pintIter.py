#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 10:06:40 2022

@author: telu
"""
import numpy as np

from blockops import BlockProblem
from blockops.plots import plotAccuracyContour, plotContour

zoom = 1
reLam = np.linspace(-3 / zoom, 0.5 / zoom, 512)
imLam = np.linspace(-3 / zoom, 3 / zoom, 512)
nBlocks = 10
nPoints = 1
schemeF = 'RK4'
nStepsF = 20
schemeG = 'RK4'
nStepsG = 1
algoName = 'Parareal'

lam = reLam[:, None] + 1j * imLam[None, :]
prob = BlockProblem(
    lam.ravel(), tEnd=nBlocks, nBlocks=nBlocks, nPoints=nPoints, scheme=schemeF,
    nStepsPerPoint=nStepsF, points='LEGENDRE', quadType='LOBATTO', form='Z2N')
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
nIterMax = nBlocks
uPar = algo(nIter=nIterMax)
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

# Plot number of iteration until discretization error
plotContour(reLam=reLam, imLam=imLam, val=nIter, nLevels=nIterMax+1, figName='PinTIter')

reqIters = np.unique(nIter).tolist()
reqIters.pop(0)


# %% Lowest cost first scheduling
speedupLCF = np.zeros(nBlocks + 1)
efficiencyLCF = np.zeros(nBlocks + 1)
for k in reqIters:
    speedupLCF[k], efficiencyLCF[k], _ = algo.getPerformances(
        N=nBlocks, K=k, nProc=nBlocks + 1, schedule_type='LCF')
nSpeedup = speedupLCF[nIter]
nEfficiency = efficiencyLCF[nIter]

# Plotting
plotContour(reLam=reLam, imLam=imLam, val=nSpeedup, 
            nLevels=None, figName='Lowest Cost First Schedule')
plotContour(reLam=reLam, imLam=imLam, val=nEfficiency, 
            nLevels=None, figName='Lowest Cost First Schedule')

# %% Block-by-Block scheduling
speedupBbB = np.zeros(nBlocks + 1)
efficiencyBbB = np.zeros(nBlocks + 1)
for k in reqIters:
    speedupBbB[k], efficiencyBbB[k], _ = algo.getPerformances(
        N=nBlocks, K=k, schedule_type='BLOCK-BY-BLOCK')
nSpeedup = speedupBbB[nIter]
nEfficiency = efficiencyBbB[nIter]

# Plotting
plotContour(reLam=reLam, imLam=imLam, val=nSpeedup, 
            nLevels=None, figName='Block-by-Block Schedule')
plotContour(reLam=reLam, imLam=imLam, val=nEfficiency, 
            nLevels=None, figName='Block-by-Block Schedule')

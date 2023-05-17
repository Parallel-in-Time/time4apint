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

nBlocks = 10
nPoints = 1
schemeF = 'RK4'
nStepsF = 20
schemeG = 'RK4'
nStepsG = 1
algoName = 'Parareal'

suffix = f'r={nStepsF/nStepsG}, G={schemeG}'

plotFineDiscrError = False
plotApproxError = False
plotNumIter = True
computeLCF = False

zoom = 1
reLam = np.linspace(-3 / zoom, 0.5 / zoom, 512)
imLam = np.linspace(-3 / zoom, 3 / zoom, 512)

lam = reLam[:, None] + 1j * imLam[None, :]
prob = BlockProblem(
    lam.ravel(), tEnd=nBlocks, nBlocks=nBlocks, nPoints=nPoints, 
    scheme='RungeKutta', rkScheme=schemeF,
    nStepsPerPoint=nStepsF, ptsType='LEGENDRE', quadType='LOBATTO')
prob.setApprox(scheme='RungeKutta', rkScheme=schemeG, nStepsPerPoint=nStepsG)

algo = prob.getBlockIteration(algoName)

# Compute fine solution
uNum = prob.getSolution('fine')

# Compute exact solution and discretization error
uExact = prob.getSolution('exact')
errDiscr = np.abs(uExact - uNum)
errDiscrMax = np.max(errDiscr, axis=(0, -1)).reshape(lam.shape)
stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
if plotFineDiscrError:
    plotAccuracyContour(reLam, imLam, errDiscrMax, stab, 
                        figName=f'discrErr, {suffix}')

# Compute approximate solution and error
uApprox = prob.getSolution('approx')
errApprox = np.abs(uNum - uApprox)
errApproxMax = np.max(errApprox, axis=(0, -1)).reshape(lam.shape)
stab = np.abs(uApprox)[0, :, -1].reshape(lam.shape)
if plotApproxError:
    plotAccuracyContour(reLam, imLam, errApproxMax, stab, 
                        figName=f'coarseErr, {suffix}')

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

if plotNumIter:
    # Plot number of iteration until discretization error
    plotContour(reLam=reLam, imLam=imLam, val=nIter, levels=None, 
                figName=f'PinTIter, {suffix}')
    plt.gcf().set_size_inches(7.56, 8.72)

reqIters = np.unique(nIter).tolist()
if 0 in reqIters:
    reqIters.remove(0)

# %% Lowest cost first scheduling
if computeLCF:
    speedupLCF = np.zeros(nBlocks + 1)
    efficiencyLCF = np.zeros(nBlocks + 1)
    for k in reqIters:
        speedupLCF[k], efficiencyLCF[k], _ = algo.getPerformances(
            N=nBlocks, K=k, nProc=nBlocks + 1, schedulerType='LCF')
    nSpeedup = speedupLCF[nIter]
    nEfficiency = efficiencyLCF[nIter]
    
    # Plotting
    plotContour(reLam=reLam, imLam=imLam, val=nSpeedup, 
                levels=None, figName=f'Lowest Cost First Schedule, {suffix}')
    plotContour(reLam=reLam, imLam=imLam, val=nEfficiency, 
                levels=None, figName=f'Lowest Cost First Schedule, {suffix}')
    plt.gcf().set_size_inches(7.56, 8.72)

# %% Block-by-Block scheduling
speedupBbB = np.zeros(nBlocks + 1)
efficiencyBbB = np.zeros(nBlocks + 1)
for k in reqIters:
    speedupBbB[k], efficiencyBbB[k], _ = algo.getPerformances(
        N=nBlocks, K=k, schedulerType='BbB')
nSpeedup = speedupBbB[nIter]
nEfficiency = efficiencyBbB[nIter]

# Plotting
plotContour(reLam=reLam, imLam=imLam, val=nSpeedup, 
            levels=None, figName=f'Block-by-Block Schedule, {suffix}')
plotContour(reLam=reLam, imLam=imLam, val=nEfficiency, 
            levels=None, figName=f'Block-by-Block Schedule, {suffix}')
plt.gcf().set_size_inches(7.56, 8.72)

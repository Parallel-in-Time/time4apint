#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

from blockops import BlockProblem
from blockops.plots import plotAccuracyContour, plotContour

zoom = 1
reLam = np.linspace(-3 / zoom, 0.5 / zoom, 256)
imLam = np.linspace(-3 / zoom, 3 / zoom, 256)
nBlocks = 6

lam = reLam[:, None] + 1j * imLam[None, :]
prob = BlockProblem(
    lam.ravel(), tEnd=nBlocks, nBlocks=nBlocks, nPoints=5, 
    scheme='Collocation', quadType='LOBATTO')
prob.setApprox('RungeKutta', rkScheme='BE')
prob.setCoarseLevel(3)


chi = prob.chi.matrix
phi = prob.phi.matrix
phiApprox = prob.phiApprox.matrix

TFtoC = prob.TFtoC.matrix
TCtoF = prob.TCtoF.matrix

phiCoarse = prob.phiCoarse.matrix
chiCoarse = prob.chiCoarse.matrix


algo = prob.getBlockIteration('PFASST')

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
plotContour(reLam=reLam, imLam=imLam, val=nIter, nLevels=None, figName='PinTIter')

reqIters = np.unique(nIter).tolist()
reqIters.pop(0)


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
            nLevels=None, figName='Block-by-Block Schedule')
plotContour(reLam=reLam, imLam=imLam, val=nEfficiency, 
            nLevels=None, figName='Block-by-Block Schedule')


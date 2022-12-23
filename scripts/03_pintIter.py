#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 10:06:40 2022

@author: telu
"""
import numpy as np
import matplotlib.pyplot as plt

from blockops import BlockProblem
from blockops.plots import plotAccuracyContour

zoom = 1
reLam = np.linspace(-4*zoom, 0.5*zoom, 501)
imLam = np.linspace(-3*zoom, 3*zoom, 500)
N = 10
M = 5
schemeF = 'COLLOCATION'
nStepsF = 40
schemeG = 'RK4'
nStepsG = 1
algoName = 'Parareal'

lam = reLam[:, None] + 1j*imLam[None, :]
prob = BlockProblem(
    lam.ravel(), N, N, M, schemeF, nStepPerNode=nStepsF)
prob.setApprox(schemeG, nStepPerNode=nStepsG)

algo = prob.getBlockIteration(algoName)

# Compute fine solution
uNum = prob.getSolution('fine')

# Compute exact solution and discretization error
uExact = prob.getSolution('exact')
errDiscr = np.abs(uExact-uNum)
errDiscrMax = np.max(errDiscr, axis=(0, -1)).reshape(lam.shape)
stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
plotAccuracyContour(reLam, imLam, errDiscrMax, stab)

# Compute approximate solution and error
uApprox = prob.getSolution('approx')
errApprox = np.abs(uExact-uApprox)
errApproxMax = np.max(errApprox, axis=(0, -1)).reshape(lam.shape)
stab = np.abs(uApprox)[0, :, -1].reshape(lam.shape)
plotAccuracyContour(reLam, imLam, errApproxMax, stab)

# Compute PinT solution and error
nIterMax = 10
uPar = algo(K=nIterMax)
errPinT = np.abs(uNum-uPar)
errPinTMax = np.max(errPinT, axis=(1, -1)).reshape(
    (errPinT.shape[0],) + (lam.shape))

# Compute required number of iteration to discretization error
nIter = -np.ones_like(errDiscrMax)
k = errPinT.shape[0]-1
for err in errPinTMax[-1::-1]:
    nIter[err < errDiscrMax] = k
    k -= 1



# %%
coords = np.meshgrid(reLam.ravel(), imLam.ravel(), indexing='ij')
levels = np.arange(nIterMax+1)

plt.figure()
plt.contourf(*coords, nIter, levels=levels)
plt.colorbar(ticks=levels)
plt.hlines(0, coords[0].min(), coords[0].max(),
           colors='black', linestyles='--')
plt.vlines(0, coords[1].min(), coords[1].max(),
           colors='black', linestyles='--')
plt.gca().set_aspect('equal', 'box')
plt.xlabel(r'$Re(\lambda)$')
plt.ylabel(r'$Im(\lambda)$')
plt.tight_layout()

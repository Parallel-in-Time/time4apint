#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 10:14:22 2023

@author: telu
"""
import numpy as np
import matplotlib.pyplot as plt

from blockops import BlockProblem

nBlocks = 10
nPoints = 1
schemeF = 'RK4'
nStepsF = 20
schemeG = 'RK4'
nStepsG = 1
algoName = 'Parareal'


alpha = 1 # From 0 (fully parabolic) to 1 (fully hyperbolic)
rhoMax = 2
nLam = 200

suffix = rf'r={nStepsF/nStepsG}, G={schemeG}, $\alpha$={alpha}'

plotFineDiscrError = False
plotApproxError = False
plotNumIter = False

rho = np.linspace(0, rhoMax, nLam)
lam = rho*np.exp(1j*np.pi*(1-alpha*0.5))
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
errDiscrMax = np.max(errDiscr, axis=(0, -1))
if plotFineDiscrError:
    plt.figure('Discr. Error')
    plt.semilogy(rho, errDiscrMax, label=suffix)
    plt.xlabel(r'$|\lambda|$')
    plt.ylabel('Max. Error')
    plt.legend()
    plt.tight_layout()


# Compute approximate solution and error
uApprox = prob.getSolution('approx')
errApprox = np.abs(uNum - uApprox)
errApproxMax = np.max(errApprox, axis=(0, -1)).reshape(lam.shape)
if plotApproxError:
    plt.figure('Approx. Error')
    plt.semilogy(rho, errApproxMax, label=suffix)
    plt.xlabel(r'$|\lambda|$')
    plt.ylabel('Max. Error')
    plt.legend()
    plt.tight_layout()
    

# Compute PinT solution and error
nIterMax = nBlocks
uPar = algo(nIter=nIterMax)
errPinT = np.abs(uNum - uPar)
errPinTMax = np.max(errPinT, axis=(1, -1)).reshape(
    (errPinT.shape[0],) + (lam.shape))

# Compute required number of iterations to discretization error
nIter = np.zeros_like(errDiscrMax, dtype=int)
k = errPinT.shape[0] - 1
for err in errPinTMax[-1::-1]:
    nIter[err < errDiscrMax] = k
    k -= 1

if plotNumIter:
    # Plot number of iteration until discretization error
    plt.figure('nIter')
    plt.plot(rho, nIter, label=suffix)
    plt.xlabel(r'$|\lambda|$')
    plt.ylabel('nIter')
    plt.legend()
    plt.tight_layout()

reqIters = np.unique(nIter).tolist()
if 0 in reqIters:
    reqIters.remove(0)

# %% Block-by-Block scheduling
speedupBbB = np.zeros(nBlocks + 1)
efficiencyBbB = np.zeros(nBlocks + 1)
for k in reqIters:
    speedupBbB[k], efficiencyBbB[k], _ = algo.getPerformances(
        N=nBlocks, K=k, schedulerType='BbB')
nSpeedup = speedupBbB[nIter]
nEfficiency = efficiencyBbB[nIter]

# Plotting
plt.figure('Block-by-Block Schedule')
plt.plot(rho, nSpeedup, label=suffix)
plt.xlabel(r'$|\lambda|$')
plt.ylabel('Speedup')
plt.legend()
plt.tight_layout()
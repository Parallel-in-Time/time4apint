#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:35:45 2022

@author: cpf5546
"""
import numpy as np
import matplotlib.pyplot as plt

from blockops.problem import BlockProblem


tEnd = 2*np.pi
lam = 1j-0.1
nBlocks = 4
nStepsF = 20
nStepsG = 1
nPoints = 1
nPointsCoarse = 1
algoName = 'PFASST'

prob = BlockProblem(lam, tEnd, nBlocks, 'RungeKutta',
                    rkScheme='BE', nPoints=nPoints, nStepsPerPoint=nStepsF)
prob.setApprox('RungeKutta', rkScheme='BE', nStepsPerPoint=nStepsG)
prob.setCoarseLevel(nPointsCoarse)


uSeq = prob.getSolution('fine', initSol=True)
uExact = prob.getSolution('exact', initSol=True)

errDiscr = prob.getError('fine', 'exact')

plt.figure(algoName)
plt.plot(uExact.ravel().real, uExact.ravel().imag, '^-', label='Exact')
plt.plot(uSeq.ravel().real, uSeq.ravel().imag, 's-', label='Sequential', ms=12)

algo = prob.getBlockIteration(algoName)

uNum = algo(nIter=4, initSol=True)

print(f'max discretization error : {errDiscr.max()}')

for k in range(4):
    plt.plot(uNum[k].ravel().real, uNum[k].ravel().imag, 'o-',
              label=f'Iter{k}')
    err = prob.getError(uNum[k][1:], 'fine')
    print(f'iter {k}, max fine error : {err.max()}')
plt.legend()
plt.show()

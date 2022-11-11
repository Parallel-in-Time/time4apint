#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:35:45 2022

@author: cpf5546
"""
import numpy as np
import matplotlib.pyplot as plt

from blockops.problem import BlockProblem


tEnd = 2*np.pi-0.2
lam = 1j
N = 8
nStepsF = 50
nStepsG = 3

prob = BlockProblem(lam, tEnd, N, 1, 'BE', nStepPerNode=nStepsF)
prob.setApprox('BE', nStepPerNode=nStepsG)


uSeq = prob.getSolution('fine', initSol=True)
uExact = prob.getSolution('exact', initSol=True)

errDiscr = prob.getError('fine', 'exact')

plt.plot(uExact.ravel().real, uExact.ravel().imag, '^-', label='Exact')
plt.plot(uSeq.ravel().real, uSeq.ravel().imag, 'o-', label='Sequential', ms=10)

parareal = prob.getBlockIteration('Parareal')

uPar = parareal(N, 4, u0=prob.u0, initSol=True)

print(f'max discretization error : {errDiscr.max()}')

for k in range(4):
    plt.plot(uPar[k].ravel().real, uPar[k].ravel().imag, 'o-',
              label=f'Iter{k}')
    errPar = prob.getError(uPar[k][1:], 'fine')
    print(f'iter {k}, max fine error : {errPar.max()}')
plt.legend()
plt.show()

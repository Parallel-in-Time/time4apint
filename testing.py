#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:35:45 2022

@author: cpf5546
"""
import numpy as np
import matplotlib.pyplot as plt

from blockops.problem import BlockProblem


tEnd = 2*np.pi-0.1
lam = 1j
N = 4
nStepsF = 20
nStepsG = 1

p = BlockProblem(lam, tEnd, N, 1, 'BE', nStepPerNode=nStepsF)
p.setApprox('BE', nStepPerNode=nStepsG)


uSeq = p.getSolution('fine', initSol=True)
uCoarse = p.getSolution('approx', initSol=True)
uExact = p.getSolution('exact', initSol=True)

plt.plot(uExact.ravel().real, uExact.ravel().imag, '^-', label='Exact')
plt.plot(uSeq.ravel().real, uSeq.ravel().imag, 'o-', label='Sequential', ms=10)

parareal = p.getBlockIteration('Parareal')

uPar = parareal(p.u0, 4, N, initSol=True)

for k in range(4):
    plt.plot(uPar[k].ravel().real, uPar[k].ravel().imag, 'o-',
              label=f'Iter{k}')

plt.legend()
plt.show()

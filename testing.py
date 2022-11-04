#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:35:45 2022

@author: cpf5546
"""
import numpy as np
import matplotlib.pyplot as plt

from blockops import BlockIteration, BlockOperator, one
from blockops.problem import BlockProblem


tEnd = 2*np.pi
lam = 1j
N = 4
nStepsF = 20
nStepsG = 2

p = BlockProblem(lam, tEnd, N, 1, 'BE', nStepPerNode=nStepsF)
p.setPhiDelta('BE', nStepPerNode=nStepsG)


uSeq = p.getFineSolution()
uCoarse = p.getDeltaSolution()
uExact = p.getExactSolution()

plt.plot(uExact.ravel().real, uExact.ravel().imag, '^-', label='Exact')
plt.plot(uSeq.ravel().real, uSeq.ravel().imag, 'o-', label='Sequential')
# plt.plot(uCoarse.ravel().real, uCoarse.ravel().imag, 'o-', label='Coarse')

parareal = p.getBlockIteration('Parareal')


uPar = parareal(p.u0, 4, N)

for k in range(2):
    plt.plot(uPar[k].ravel().real, uPar[k].ravel().imag, 'o-',
             label=f'Iter{k}')

plt.legend()

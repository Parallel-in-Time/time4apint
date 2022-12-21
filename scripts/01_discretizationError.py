#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:42:11 2022

@author: cpf5546
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

from blockops import BlockProblem

reLam = np.linspace(-4, 0.5, 500)
imLam = np.linspace(-3, 3, 500)
N = 1
M = 5
scheme = 'COLLOCATION'

lam = reLam[:, None] + 1j*imLam[None, :]
prob = BlockProblem(
    lam.ravel(), N, N, M, scheme,
    nodes='LEGENDRE', qType='LOBATTO')

uExact = prob.getSolution('exact')
uNum = prob.getSolution('fine')
err = np.abs(uExact-uNum)

stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
errEnd = err[-1, :, -1].reshape(lam.shape)
errMax = np.max(err, axis=(0, -1)).reshape(lam.shape)

err = errMax

# Plot discretization error on complex plane
coords = np.meshgrid(reLam.ravel(), imLam.ravel(), indexing='ij')

plt.figure()
eMin = -7
eMax = 0
levels = np.logspace(eMin, eMax, num=22)
err[err < 10**eMin] = 10**eMin
err[err > 10**eMax] = 10**eMax
ticks = [10**(i) for i in range(eMin, eMax+1)]
plt.contourf(*coords, err, levels=levels, locator=ticker.LogLocator())
plt.colorbar(ticks=ticks, format=ticker.LogFormatter())
CS = plt.contour(*coords, err, levels=ticks,
                 colors='k', linestyles='--', linewidths=0.75)
plt.contour(*coords, stab, levels=[1], colors='gray')
plt.hlines(0, reLam.min(), reLam.max(), colors='black', linestyles='--')
plt.vlines(0, imLam.min(), imLam.max(), colors='black', linestyles='--')
plt.gca().set_aspect('equal', 'box')
plt.xlabel(r'$Re(\lambda)$')
plt.ylabel(r'$Im(\lambda)$')
plt.tight_layout()

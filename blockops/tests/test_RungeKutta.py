#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 09:03:52 2023

@author: cpf5546
"""
import pytest
import numpy as np

from blockops.schemes import STABILITY_FUNCTION_RK

EXPECTED_ORDER = {
    ('BE', 'FE', 'RK21'): 1,
    ('TRAP', 'RK2', 'SDIRK2'): 2,
    ('RK3', 'RK53', 'SDIRK3'): 3,
    ('RK4', 'GAUSS-LG', 'SDIRK54'): 4,
    ('RK65',): 5}

nSteps = 2**np.arange(3, 7)[-1::-1]


def numericalOrder(nSteps, err):
    """Help function to compute numerical order using Dahlquist"""

    x, y = np.log10(1/nSteps), np.log10(err)

    # Compute regression coefficients and rmse
    xMean = x.mean()
    yMean = y.mean()
    sX = ((x-xMean)**2).sum()
    sXY = ((x-xMean)*(y-yMean)).sum()

    beta = sXY/sX
    alpha = yMean - beta*xMean

    yHat = alpha + beta*x
    rmse = ((y-yHat)**2).sum()**0.5
    rmse /= x.size**0.5

    return beta, rmse


@pytest.mark.parametrize("lam", [-1, 1j, 1j-1])
def testNumericalOrder(lam):
    """Test expected order for all RK methods"""

    for schemes, order in EXPECTED_ORDER.items():
        for scheme in schemes:
            g = STABILITY_FUNCTION_RK[scheme]

            uNum = []
            for n in nSteps:
                uNum.append(g(lam/n)**n)

            err = np.abs(np.array(uNum)-np.exp(lam))
            beta, rmse = numericalOrder(nSteps, err)

            assert rmse < 0.02, f"rmse to high ({rmse}) for {scheme}"
            assert abs(beta-order) < 0.1, f"wrong numerical order ({beta}) for {scheme}"

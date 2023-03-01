#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import numpy as np

from blockops.schemes import STABILITY_FUNCTION_RK
from blockops.utils import numericalOrder

EXPECTED_ORDER = {
    1: ('BE', 'FE', 'RK21'),
    2: ('TRAP', 'RK2', 'SDIRK2'),
    3: ('RK3', 'RK53', 'SDIRK3'),
    4: ('RK4', 'GAUSS-LG', 'SDIRK54'),
    5: ('RK65',)}

nSteps = 2**np.arange(3, 7)[-1::-1]

RK_ORDERS = {
    scheme: order 
    for order, schemes in EXPECTED_ORDER.items() 
    for scheme in schemes}

lamValues = [-1, 1j, 1j-1]
lamStrings = [f'lambda={lam}' for lam in lamValues]

@pytest.mark.parametrize("lam", lamStrings)
@pytest.mark.parametrize("scheme", RK_ORDERS.keys())
def testNumericalOrder(lam, scheme):
    """Test expected order for all RK methods"""
    lam = eval(lam.split('=')[-1])

    g = STABILITY_FUNCTION_RK[scheme]
    order = RK_ORDERS[scheme]

    uNum = []
    for n in nSteps:
        uNum.append(g(lam/n)**n)

    err = np.abs(np.array(uNum)-np.exp(lam))
    beta, rmse = numericalOrder(nSteps, err)

    assert rmse < 0.02, f"rmse to high ({rmse}) for {scheme}"
    assert abs(beta-order) < 0.1, f"wrong numerical order ({beta}) for {scheme}"

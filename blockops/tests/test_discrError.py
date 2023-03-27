#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import numpy as np

from blockops.problem import BlockProblem
from blockops.utils.numeric import numericalOrder

COLLOCATION_ORDERS = {
    'GAUSS': 
        (lambda M: 2*M,     # with collocation update
         lambda M: M-1),    # no collocation update
    'RADAU-RIGHT': 
        (lambda M: 2*M-1,   # with collocation update
         lambda M: 2*M-1),  # no collocation update
    'RADAU-LEFT': 
        (lambda M: 2*M-1,   # with collocation update
         lambda M: M-1),    # no collocation update
    'LOBATTO': 
         (lambda M: 2*M-2,  # with collocation update
          lambda M: 2*M-2)  # no collocation update
    }
    
COLLOCATION_STEPS = {
    2: 
        [128, 64, 32],
    3: 
        [64, 32, 16],
    4: 
        [32, 16, 8],
    }

T = 2*np.pi
lamValues = [-1, 1j, 1j-1]
lamStrings = [f'lambda={lam}' for lam in lamValues]

@pytest.mark.parametrize("lam", lamStrings)
@pytest.mark.parametrize("collUpdate", ['collUpdate', 'noCollUpdate'])
@pytest.mark.parametrize("M", COLLOCATION_STEPS.keys())
@pytest.mark.parametrize("quadType", COLLOCATION_ORDERS.keys())
def testCollocationOrder(lam, collUpdate, M, quadType):
    """Test expected order for all collocation methods"""
    
    lam = eval(lam.split('=')[-1])
    collUpdate = True if collUpdate == 'collUpdate' else False
    nPoints = M+1 if collUpdate else M
    order = COLLOCATION_ORDERS[quadType][0 if collUpdate else 1](M)
    
    nSteps = np.array(COLLOCATION_STEPS[M])
    
    err = []
    for nStep in nSteps:
        prob = BlockProblem(
            lam, T, nStep, nPoints, 'Collocation', 
            quadType=quadType, collUpdate=collUpdate)
        err.append(prob.getError().ravel()[-1])
    err = np.array(err)
        
    beta, rmse = numericalOrder(nSteps, err)
    
    assert rmse < 0.05, f"rmse to high ({rmse})"
    assert abs(beta-order) < 0.3, f"wrong numerical order ({beta}), expected {order}"

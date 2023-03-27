#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 13:13:41 2023

@author: cpf5546
"""
import numpy as np
from blockops.problem import BlockProblem

tEnd = 2*np.pi
lam = 1j
N = 8

def testBasics():
    prob = BlockProblem(lam, tEnd, N, 5, 'RungeKutta', rkScheme='BE',
                        quadType='LOBATTO', form='N2N', nStepsPerPoint=5)
    prob.setCoarseLevel(3)
    prob.setApprox('RungeKutta', rkScheme='BE', nStepsPerPoint=1)
    prob.setCoarseApprox()

    assert prob.noDeltaChi, "non null deltaChi operator"
    assert prob.invariantCoarseProlong, "non invariant coarse prolongation"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 18:13:46 2023

@author: telu
"""
import sympy as sy

from blockops.problem import BlockProblem

# Dummy problem
prob = BlockProblem(1, 1, 3, 1, 'BE')
prob.setApprox('BE')
prob.setCoarseLevel(1)

algo = prob.getBlockIteration('PFASST')

B00 = algo.blockCoeffs[(0, 0)].symbol
B01 = algo.blockCoeffs[(0, 1)].symbol
B10 = algo.blockCoeffs[(1, 0)].symbol

u00, u01, u10 = sy.symbols('u_0^0, u_0^1, u_1^0', commutative=False)

expr = B00*u00 + B01*u01 + B10*u10
e1 = expr.expand()


c1 = algo.blockOps[r'\tilde{\phi}_C'].symbol**(-1)
c2 = algo.blockOps[r'\tilde{\phi}'].symbol**(-1)



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:35:45 2022

@author: cpf5546
"""
import numpy as np

from blockops import BlockIteration, BlockOperator, one
from blockops.problem import BlockProblem


tEnd = 2*np.pi
lam = 1j
N = 4
nStepsF = 4
nStepsG = 2

p = BlockProblem(lam, tEnd, N, nStepsF, 'BE')

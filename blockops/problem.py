#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:56:41 2022

@author: cpf5546
"""
import numpy as np

from .schemes import getBlockMatrices
from .block import BlockOperator

class BlockProblem(object):

    def __init__(self, lam, tEnd, N, M, scheme, u0=1, **schemeArgs):

        # Block sizes and problem settings
        self.N, self.M = N, M
        self.dt = tEnd/N
        self.lamDt = lam*self.dt

        # Set up bock operators and propagator
        phi, chi, nodes = getBlockMatrices(self.lamDt, M, scheme, **schemeArgs)
        self.phi = BlockOperator(r'$\phi$', matrix=phi)
        self.chi = BlockOperator(r'$\chi$', matrix=chi)
        self.prop = self.phi**(-1) * self.chi

        # Initial solution
        self.u0 = np.ones(M)*u0

    def getFineSolution(self):
        return

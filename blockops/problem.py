#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:56:41 2022

@author: cpf5546
"""
import numpy as np

from .schemes import getBlockMatrices, getTransferMatrices
from .block import BlockOperator
from .iteration import ALGORITHMS


class BlockProblem(object):

    def __init__(self, lam, tEnd, N, M, scheme, u0=1, **schemeArgs):

        # Block sizes and problem settings
        self.N, self.M = N, M
        self.dt = tEnd/N
        self.lam = lam

        # Set up bock operators and propagator of the sequential problem
        phi, chi, nodes, cost, form = getBlockMatrices(
            lam*self.dt, M, scheme, **schemeArgs)
        self.phi = BlockOperator(r'$\phi$', matrix=phi, cost=cost)
        self.chi = BlockOperator(r'$\chi$', matrix=chi, cost=0)
        self.prop = self.phi**(-1) * self.chi
        self.nodes = nodes
        self.scheme = scheme
        self.form = form

        # Storage for approximate and coarse block operators
        self.phiDelta = None
        self.schemeDelta = None
        self.propDelta = None

        self.phiCoarse = None
        self.chiCoarse = None
        self.nodesCoarse = None
        self.TFtoC = None
        self.TCtoF = None
        self.deltaChi = None

        self.phiDeltaCoarse = None
        self.methodDeltaCoarse = None

        # Problem parameters
        self.u0 = np.ones(M)*u0 + 0*lam

    @property
    def times(self):
        return np.array([[(i+tau)*self.dt for tau in self.nodes]
                         for i in range(self.N)])

    @property
    def uShape(self):
        return (self.N, self.M)

    def setApprox(self, scheme, **schemeArgs):
        phi, _, _, cost, _ = getBlockMatrices(
            self.lam*self.dt, self.M, scheme, nodes=self.nodes, form=self.form,
            **schemeArgs)
        self.phiDelta = BlockOperator(r'$\phi_{Delta}$', matrix=phi, cost=cost)
        self.schemeDelta = scheme
        self.propDelta = self.phiDelta**(-1) * self.chi

    def setCoarseLevel(self, M):
        phi, chi, nodes, cost, _ = getBlockMatrices(
            self.lam*self.dt, M, self.method, form=self.form)
        self.nodesCoarse = nodes
        self.phiCoarse = BlockOperator(
            r'$\tilde{\phi}$', matrix=phi, cost=cost)
        TFtoC, TCtoF = getTransferMatrices(self.nodes, self.nodesCoarse)
        self.TFtoC = BlockOperator('$T_F^C$', matrix=TFtoC, cost=0)
        self.TCtoF = BlockOperator('$T_C^F$', matrix=TCtoF, cost=0)
        # TODO : add deltaChi

    def getSolution(self, sType='fine', initSol=False):
        u = [self.u0]

        if sType == 'exact':
            uTh = np.exp(self.lam*self.times)*self.u0[0]
            if initSol:
                return np.array(u + uTh.tolist())
            else:
                return uTh

        if sType == 'fine':
            prop = self.prop
        elif sType == 'approx':
            prop = self.propDelta
        for i in range(self.N):
            u.append(prop(u[-1]))

        if initSol:
            return np.array(u)
        else:
            return np.array(u[1:])

    def getError(self, uNum='fine', uRef='exact'):
        if isinstance(uRef, str):
            if uRef == 'exact':
                uRef = self.getSolution('exact')
            elif uRef == 'fine':
                uRef = self.getSolution('fine')
        if isinstance(uNum, str):
            if uNum == 'fine':
                uNum = self.getSolution('fine')
        return np.abs(uNum - uRef)

    def getBlockIteration(self, algo):
        try:
            BlockIter = ALGORITHMS[algo]
            blockIter = BlockIter(
                phi=self.phi, phiDelta=self.phiDelta, chi=self.chi)
            blockIter.problem = self
            return blockIter
        except KeyError:
            raise NotImplementedError(
                f'block iteration for {algo} not implemented')

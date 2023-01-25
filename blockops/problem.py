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
        phi, chi, points, cost, form = getBlockMatrices(
            lam*self.dt, M, scheme, **schemeArgs)
        self.phi = BlockOperator(r'\phi', matrix=phi, cost=cost)
        self.chi = BlockOperator(r'\chi', matrix=chi, cost=0)
        self.prop = self.phi**(-1) * self.chi
        self.points = points
        self.scheme = scheme
        self.form = form

        # Storage for approximate and coarse block operators
        self.phiApprox= None
        self.schemeApprox = None
        self.propApprox = None

        self.phiCoarse = None
        self.chiCoarse = None
        self.pointsCoarse = None
        self.TFtoC = None
        self.TCtoF = None
        self.deltaChi = None

        self.phiApproxCoarse = None
        self.methodApproxCoarse = None

        # Problem parameters
        self.u0 = np.ones_like(u0*lam, shape=(1, M))
        if np.size(lam) == 1:
            self.u0 = self.u0.squeeze(axis=0)

    @property
    def nLam(self):
        return np.size(self.lam)

    @property
    def times(self):
        return np.array([[(i+tau)*self.dt for tau in self.points]
                         for i in range(self.N)])

    @property
    def uShape(self):
        if self.nLam == 1:
            return (self.N, self.M)
        else:
            return (self.N, self.nLam, self.M)

    def setApprox(self, scheme, **schemeArgs):
        phi, _, _, cost, _ = getBlockMatrices(
            self.lam*self.dt, self.M, scheme, points=self.points, form=self.form,
            **schemeArgs)
        self.phiApprox = BlockOperator(r'\phi_{Delta}', matrix=phi, cost=cost)
        self.schemeApprox = scheme
        self.propApprox = self.phiApprox**(-1) * self.chi

    @property
    def approxSet(self):
        for attr in ['phiApprox', 'schemeApprox', 'propApprox']:
            if getattr(self, attr) is None:
                return False
        return True

    def setCoarseLevel(self, M):
        phi, chi, points, cost, _ = getBlockMatrices(
            self.lam*self.dt, M, self.method, form=self.form)
        self.pointsCoarse = points
        self.phiCoarse = BlockOperator(
            r'\tilde{\phi}', matrix=phi, cost=cost)
        TFtoC, TCtoF = getTransferMatrices(self.points, self.pointsCoarse)
        self.TFtoC = BlockOperator('T_F^C', matrix=TFtoC, cost=0)
        self.TCtoF = BlockOperator('T_C^F', matrix=TCtoF, cost=0)
        # TODO : add deltaChi

    def getSolution(self, sType='fine', initSol=False):
        u = [self.u0]

        if sType == 'exact':
            lamT = self.lam*self.times if self.nLam == 1 else \
                self.lam[None, :, None] * self.times[:, None, :]
            uTh = np.exp(lamT)*self.u0[0]
            if initSol:
                return np.array(u + uTh.tolist())
            else:
                return uTh

        if sType == 'fine':
            prop = self.prop
        elif sType == 'approx':
            prop = self.propApprox
        else:
            raise NotImplementedError(f'sType={sType}')
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
            if not self.approxSet:
                raise ValueError('Approximation not set for the problem')
            blockIter = BlockIter(
                phi=self.phi, phiApprox=self.phiApprox, chi=self.chi)
            blockIter.prob = self
            return blockIter
        except KeyError:
            raise NotImplementedError(
                f'block iteration for {algo} not implemented')

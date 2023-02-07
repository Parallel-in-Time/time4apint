#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 15:56:41 2022

@author: cpf5546
"""
import numpy as np

from .schemes import getBlockMatrices, getTransferMatrices
from .block import BlockOperator
from .iteration import ALGORITHMS, BlockIteration


class ProblemError(Exception):
    pass

class BlockProblem(object):

    def __init__(self, lam, tEnd, nBlocks, nPoints, scheme, u0=1,
                 **schemeArgs):

        # Block sizes and problem settings
        self.nBlocks = nBlocks
        self.dt = tEnd/nBlocks
        self.lam = lam

        # Set up bock operators and propagator of the sequential problem
        phi, chi, points, cost, params, paramsPoints = getBlockMatrices(
            lam*self.dt, nPoints, scheme, **schemeArgs)
        self.phi = BlockOperator(r'\phi', matrix=phi, cost=cost)
        self.chi = BlockOperator(r'\chi', matrix=chi, cost=0)

        self.points = points
        self.paramsPoints = paramsPoints
        self.params = params

        # Storage for approximate operator and parameters
        self.phiApprox= None
        self.paramsApprox = None

        # Storage for coarse operators
        self.phiCoarse = None
        self.chiCoarse = None
        self.pointsCoarse = None
        self.TFtoC = None
        self.TCtoF = None
        self.deltaChi = None

        # Storage for coarse approximate operator and parameters
        self.phiCoarseApprox = None
        self.paramsCoarseApprox = None
        self.paramsCoarsePoints = None

        # Additional storage for propagators
        self.prop = self.phi**(-1) * self.chi
        self.propApprox = None
        self.propCoarse = None
        self.propCoarseApprox = None

        # Problem parameters
        self.u0 = np.ones_like(u0*lam, shape=(1, nPoints))
        if np.size(lam) == 1:
            self.u0 = self.u0.squeeze(axis=0)

    @property
    def nLam(self):
        return np.size(self.lam)

    @property
    def nPoints(self):
        return np.size(self.points)

    @property
    def times(self):
        return np.array([[(i+tau)*self.dt for tau in self.points]
                         for i in range(self.nBlocks)])

    @property
    def uShape(self):
        if self.nLam == 1:
            return (self.nBlocks, self.nPoints)
        else:
            return (self.nBlocks, self.nLam, self.nPoints)

    def setApprox(self, scheme, **schemeArgs):
        phi, _, _, cost, params, _ = getBlockMatrices(
            self.lam*self.dt, None, scheme, points=self.points,
            form=self.params['form'], **schemeArgs)
        self.phiApprox = BlockOperator(r'\tilde{\phi}', matrix=phi, cost=cost)
        self.paramsApprox = params
        self.propApprox = self.phiApprox**(-1) * self.chi
        try:
            self.setCoarseApprox()
        except ProblemError:
            pass

    @property
    def approxIsSet(self):
        for attr in ['phiApprox', 'propApprox', 'paramsApprox']:
            if getattr(self, attr) is None:
                return False
        return True

    def setCoarseLevel(self, points, **paramsPoints):
        localParams = self.paramsPoints.copy()
        localParams.update(paramsPoints)
        if isinstance(points, int):
            grid = {'nPoints': points, **localParams}
        else:
            grid = {'nPoints': len(points), 'points': points}
        phi, chi, points, cost, _, paramsPoints = getBlockMatrices(
            self.lam*self.dt, **grid, **self.params)
        self.pointsCoarse = points
        self.paramsCoarsePoints = paramsPoints
        self.phiCoarse = BlockOperator(r'\phi_C', matrix=phi, cost=cost)
        self.chiCoarse = BlockOperator(r'\chi_C', matrix=chi, cost=0)

        TFtoC, TCtoF = getTransferMatrices(self.points, self.pointsCoarse)
        self.TFtoC = BlockOperator('T_F^C', matrix=TFtoC, cost=0)
        self.TCtoF = BlockOperator('T_C^F', matrix=TCtoF, cost=0)
        self.deltaChi = self.TFtoC * self.chi - self.chiCoarse * self.TFtoC
        try:
            self.setCoarseApprox()
        except ProblemError:
            pass

    @property
    def coarseIsSet(self):
        for attr in ['pointsCoarse', 'phiCoarse', 'chiCoarse',
                     'TFtoC', 'TCtoF', 'deltaChi']:
            if getattr(self, attr) is None:
                return False
        return True

    @property
    def noDeltaChi(self):
        if self.coarseIsSet:
            return np.linalg.norm(self.deltaChi.matrix, ord=np.inf) < 1e-14

    @property
    def nPointsCoarse(self):
        if self.coarseIsSet:
            return np.size(self.pointsCoarse)

    @property
    def invariantCoarseProlong(self):
        if self.coarseIsSet:
            transfer = (self.TFtoC * self.TCtoF).matrix
            return np.allclose(transfer, np.eye(self.nPointsCoarse))

    def setCoarseApprox(self, **params):
        if not (self.coarseIsSet and self.approxIsSet):
            raise ProblemError(
                'cannot set coarse approximate operators before both coarse'
                ' level and approximation are set')
        localParams = self.paramsApprox.copy()
        localParams.update(params)
        phi, _, _, cost, params, _ = getBlockMatrices(
            self.lam*self.dt, None, points=self.pointsCoarse, **localParams)
        self.phiCoarseApprox = BlockOperator(r'\tilde{\phi}_C', matrix=phi, cost=cost)
        self.paramsCoarseApprox = params

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
        for i in range(self.nBlocks):
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

    def getBlockIteration(self, algo: str) -> BlockIteration:
        try:
            BlockIter = ALGORITHMS[algo]
            if BlockIter.needApprox and not self.approxIsSet:
                raise ValueError(f'{algo} need an approximate block operator')
            if BlockIter.needCoarse and not self.coarseIsSet:
                raise ValueError(f'{algo} need a coarse block operator')
            blockIter = BlockIter(
                phi=self.phi, phiApprox=self.phiApprox, chi=self.chi,
                phiCoarse=self.phiCoarse, chiCoarse=self.chiCoarse,
                TFtoC=self.TFtoC, TCtoF=self.TCtoF,
                phiCoarseApprox=self.phiCoarseApprox)
            blockIter.prob = self
            return blockIter
        except KeyError:
            raise NotImplementedError(
                f'block iteration for {algo} not implemented')

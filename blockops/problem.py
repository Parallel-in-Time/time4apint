#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

from blockops.schemes import getBlockMatrices, getTransferMatrices
from blockops.block import BlockOperator
from blockops.iteration import ALGORITHMS, BlockIteration

class ProblemError(Exception):
    """Specific exception for the BlockProblem class"""
    pass

class BlockProblem(object):
    r"""
    Class instantiating a block problem for the Dahlquist problem
    
    .. math::
        \frac{du}{dt} = \lambda u, \quad
        \lambda \in \mathbb{C}, \quad
        t \in [0, T], \quad 
        u(0) = u_0
        
    for one or several values of :math:`\lambda`.
    The block problem has the form :
        
    .. math::
        \begin{pmatrix}
            \phi & & &\\
            -\chi & \phi & & \\
            & \ddots & \ddots & \\
            & & -\chi & \phi
        \end{pmatrix}
        \begin{bmatrix}
            {\bf u}_1\\{\bf u}_2\\\vdots\\{\bf u}_N
        \end{bmatrix}
        =
        \begin{bmatrix}
            \chi(u_0{\bf e})\\0\\\vdots\\0
        \end{bmatrix}

    With :math:`\phi` and :math:`\chi` the block operator of size :math:`(M,M)`
    such that

    .. math::
        \phi {\bf u}_{n+1} = \chi {\bf u}_n

    Parameters
    ----------
    lam : float, complex or np.1darray
        Lambda values.
    tEnd : float
        End of simulation interval :math:`T`.
    nBlocks : int
        Number of blocks :math:`N`.
    nPoints : int
        Number of time-points per block :math:`M`.
    scheme : str
        Time discretization scheme used for the block operators.
    u0 : scalar, optional
        The initial solution :math:`u_0`. The default is 1.
    **schemeArgs :
        Additional keyword arguments used for the time-discretization scheme
        (see doc of blockops.schemes.getBlockMatrices).
    """
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
        """Number of lambda values for the block problem"""
        return np.size(self.lam)

    @property
    def nPoints(self):
        """Number of time points in each blocks"""
        return np.size(self.points)

    @property
    def times(self):
        """2D vector with time values (nBlocks, nPoints)"""
        return np.array([[(i+tau)*self.dt for tau in self.points]
                         for i in range(self.nBlocks)])

    @property
    def uShape(self):
        """Shape of the global u vector for each block"""
        if self.nLam == 1:
            return (self.nBlocks, self.nPoints)
        else:
            return (self.nBlocks, self.nLam, self.nPoints)

    # -------------------------------------------------------------------------
    # Method for approximate operator
    # -------------------------------------------------------------------------
    def setApprox(self, scheme, **schemeArgs):
        r"""
        Set the approximate block operator :math:`\tilde{\phi}`
        on the fine level.

        Parameters
        ----------
        scheme : str
            Time discretization scheme for the approximate block operator.
        **schemeArgs :
            Additional keyword arguments used for the time-discretization scheme
            (see doc of blockops.schemes.getBlockMatrices).
        """
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
        """Wether or not the approximate operator is defined on fine level"""
        for attr in ['phiApprox', 'propApprox', 'paramsApprox']:
            if getattr(self, attr) is None:
                return False
        return True
    
    # -------------------------------------------------------------------------
    # Method for coarse level operators
    # -------------------------------------------------------------------------
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
        
        self.propCoarse = self.TCtoF * self.phiCoarse**(-1) * self.chiCoarse * self.TFtoC
        try:
            self.setCoarseApprox()
        except ProblemError:
            pass

    @property
    def coarseIsSet(self):
        """Wether or not coarse level and its operators are defined"""
        for attr in ['pointsCoarse', 'phiCoarse', 'chiCoarse',
                     'TFtoC', 'TCtoF', 'deltaChi',
                     'propCoarse']:
            if getattr(self, attr) is None:
                return False
        return True

    @property
    def noDeltaChi(self):
        r"""Wether or not :math:`\Delta_\chi = T_F^C\chi - \chi^C T_C^F` is null"""
        if self.coarseIsSet:
            return np.linalg.norm(self.deltaChi.matrix, ord=np.inf) < 1e-14

    @property
    def nPointsCoarse(self):
        """Number of points per block for the coarse level"""
        if self.coarseIsSet:
            return np.size(self.pointsCoarse)

    @property
    def invariantCoarseProlong(self):
        """Wether or not :math:`T_F^C T_C^F = I`"""
        if self.coarseIsSet:
            transfer = (self.TFtoC * self.TCtoF).matrix
            return np.allclose(transfer, np.eye(self.nPointsCoarse))
        
    @property
    def timesCoarse(self):
        """2D vector with coarse time values (nBlocks, nPointsCoarse)"""
        return np.array([[(i+tau)*self.dt for tau in self.pointsCoarse]
                         for i in range(self.nBlocks)])

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
        
        self.propCoarseApprox = self.TCtoF * self.phiCoarseApprox**(-1) * self.chiCoarse * self.TFtoC

    # -------------------------------------------------------------------------
    # Method for solutions and errors
    # -------------------------------------------------------------------------
    def getSolution(self, sType='fine', initSol=False) -> np.ndarray:
        """
        Get a specific solution from the block problem.

        Parameters
        ----------
        sType : str, optional
            DESCRIPTION. The default is 'fine'.
        initSol : bool, optional
            Wether or not include the :math:`u_0` term. 
            The default is False.

        Returns
        -------
        sol : np.ndarray
            The solution in array form (shape self.uShape).
        """
        u = [self.u0]

        # Exact solution using exponential
        if sType == 'exact':
            lamT = self.lam*self.times if self.nLam == 1 else \
                self.lam[None, :, None] * self.times[:, None, :]
            uTh = np.exp(lamT)*self.u0[0]
            if initSol:
                return np.array(u + uTh.tolist())
            else:
                return uTh

        # Build the propagator depending on the selected solution type
        if sType == 'fine':
            prop = self.prop
        elif sType == 'approx':
            prop = self.propApprox
        elif sType == 'coarse':
            prop = self.propCoarse
        elif sType == 'coarseApprox':
            prop = self.propCoarseApprox
        else:
            raise NotImplementedError(f'sType={sType}')
            
        # Propagate solution (serial)
        for i in range(self.nBlocks):
            u.append(prop(u[-1]))

        if initSol:
            return np.array(u)
        else:
            return np.array(u[1:])

    def getError(self, uNum='fine', uRef='exact') -> np.ndarray:
        """
        Compute the (absolute) error between two solutions.

        Parameters
        ----------
        uNum : str or np.ndarray, optional
            Solution from which to compute the error.
            Either a solution type returned by getSolution,
            or some solution values in array form. 
            The default is 'fine'.
        uRef : str or np.ndarray, optional
            Reference solution for the error computation.
            Either a solution type returned by getSolution,
            or some solution values in array form. The default is 'fine'.

        Returns
        -------
        err : np.ndarray
            The error in array form (shape self.uShape).
        """
        if isinstance(uRef, str):
            uRef = self.getSolution(uRef)
        if isinstance(uNum, str):
            uNum = self.getSolution(uNum)
        return np.abs(uNum - uRef)

    # -------------------------------------------------------------------------
    # Method for block iterations
    # -------------------------------------------------------------------------
    def getBlockIteration(self, algo: str) -> BlockIteration:
        """
        Generate a block iteration object associated to the block problem.

        Parameters
        ----------
        algo : str
            Type of algorithm to use (Parareal, ABGS, TMG, PFASST, ...)

        Returns
        -------
        BlockIteration
            The block iteration object.
        """
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
            
            
            
if __name__ == '__main__':
    # Quick module testing
    
    # Create block problem with its fine level operator
    prob = BlockProblem(1j, 12*np.pi, nBlocks=6, nPoints=11, scheme='SDIRK54')
    # Set up coarse level :
    prob.setCoarseLevel(points=5)
    # Set up approximate operator (on coarse and fine level) :
    prob.setApprox('SDIRK2')
    
    import matplotlib.pyplot as plt

    # Get time vector and add t=0
    times = prob.times.ravel()
    times = np.concatenate(([0], times))
    
    # Compute and plot exact solution
    u = prob.getSolution('exact').ravel()
    u = np.concatenate(([1], u))
    plt.plot(times, u.real, 'o--', label='exact')
    
    for sType in ['fine', 'approx', 'coarse', 'coarseApprox']:
        u = prob.getSolution(sType).ravel()
        u = np.concatenate(([1], u))
        plt.plot(times, u.real, label=sType)
        
    plt.legend()

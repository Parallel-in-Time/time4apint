#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 17:27:18 2023

Class implementing a BlockScheme object for Runge-Kutta methods
"""
import numpy as np

from blockops.utils.vectorize import matMatMul
from blockops.schemes import BlockScheme, register
from blockops.utils.params import setParams, MultipleChoices, PositiveInteger



STABILITY_FUNCTIONS = {
    # First order methods
    'BE': lambda z: (1 - z)**(-1),
    'FE': lambda z: 1 + z,
    'RK21': lambda z: 1 + z + z**2,
    # Second order methods
    'TRAP': lambda z: (1 + z/2)/(1 - z/2),
    'RK2': lambda z: 1 + z + z**2/2,
    'GAUSS-LG': lambda z: (1 + z/2 + z**2/12)/(1 - z/2 + z**2/12),
    'SDIRK2': lambda z: (0.414213562373095*z + 1) /
        (0.0857864376269049*z**2 - 0.585786437626905*z + 1),
    # Third order methods
    'RK3': lambda z: 1 + z + z**2/2 + z**3/6,
    'RK53': lambda z: 1 + z + z**2/2 + z**3/6 + z**4/26 + z**5/182,
    'SDIRK3': lambda z: (-0.237660690809725*z**2 - 0.307599564525379*z + 1) /
        (-0.0828057581196304*z**3 + 0.569938873715654*z**2
         - 1.30759956452538*z + 1),
    # Fourth order methods
    'RK4': lambda z: 1 + z + z**2/2 + z**3/6 + z**4/24,
    'SDIRK54': lambda z: (0.00258844870108142*z**8 + 0.0122346760314181*z**7
                          - 0.0195644048996919*z**6 - 0.202186867042821*z**5
                          - 0.0641999421296173*z**4 + 0.999095775462969*z**3
                          + 71/72*z**2 - 41/48*z - 1) /
        ((1 - z/4)**5*(0.283989800347222*z**4 + 1.01775896990741*z**3 +
                       337/576*z**2 - 53/48*z - 1)),
    # Fith order method
    'RK65': lambda z: 1 + z + z**2/2 + z**3/6 + z**4/24 + z**5/120 + z**6/1280,
    # Exact integration (infinite order)
    'EXACT': lambda z: np.exp(z)}

N_STAGES = {
    'FE': 2,
    'RK21': 2,
    'RK2': 2,
    'RK3': 3,
    'RK53': 5,
    'RK4': 4,
    'RK65': 6}


@register
@setParams(
    rkScheme=MultipleChoices(*STABILITY_FUNCTIONS.keys(), latexName=r'\text{Scheme}'),
    nStepsPerPoint=PositiveInteger(latexName=r'\ell')
    )
class RungeKutta(BlockScheme):
    """
    Generic class for Runge-Kutta schemes

    Parameters
    ----------
    rkScheme : str, optional
        Name of the Runge-Kutta scheme (BE, FE, TRAP, RK4, ...).
    nStepsPerPoint : int, optional
        Number of time-steps per block time point.
    """
    def __init__(self, nPoints, ptsType='EQUID', quadType='LOBATTO', form='Z2N',
                 rkScheme='BE', nStepsPerPoint=1):
        self.initialize(locals())
        super().__init__(nPoints, ptsType, quadType, form)

    def getBlockMatrices(self, lamDt):
        """
        Generate matrices for the :math:`\phi` and :math:`\chi` block operators.

        Parameters
        ----------
        lamDt : scalar or 1D vector
            The value of :math:`\lambda\Delta{T}` for the block.

        Returns
        -------
        phi : np.ndarray
            The matrix for :math:`\phi`.
        chi : np.ndarray
            The matrix for :math:`\chi`.
        """
        # Main parameters
        rkScheme = self.PARAMS['rkScheme'].value
        nStepsPerPoint = self.PARAMS['nStepsPerPoint'].value
        form = self.PARAMS['form'].value
        deltas = self.deltas
        nPoints = self.nPoints

        # Compute amplification factor
        z = lamDt*deltas/nStepsPerPoint
        R = STABILITY_FUNCTIONS[rkScheme](z)**(-nStepsPerPoint)

        # Build phi and chi matrices
        phi = np.zeros_like(R, shape=(nPoints,)+R.shape)
        phi[np.diag_indices(nPoints)] = R
        phi[1:,:-1][np.diag_indices(nPoints-1)] = -1
        chi = np.zeros_like(R, shape=(nPoints, nPoints))
        chi[0, -1] = 1
        chi = chi[..., None]

        # Eventually switch to zero-to-node formulation
        if form == 'Z2N':
            T = np.tril(np.ones((nPoints, nPoints)))
            phi = matMatMul(T, phi)
            chi = matMatMul(T, chi)

        return phi, chi

    def getBlockCosts(self):
        """
        Generate costs fpr the :math:`\phi` and :math:`\chi` block operators.

        Returns
        -------
        costPhi : float
            The (estimated) cost for :math:`\phi`.
        costChi : float
            The (estimated) cost for :math:`\chi`.
        """
        costPhi = self.PARAMS['nStepsPerPoint'].value * self.nPoints
        if self.PARAMS['rkScheme'] in N_STAGES:
            costPhi *= N_STAGES[self.PARAMS['rkScheme']]
        costChi = 0
        return costPhi, costChi

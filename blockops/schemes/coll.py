#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 17:27:30 2023

Class implementing a BlockScheme object for Collocation methods
"""
import numpy as np

from blockops.utils.poly import LagrangeApproximation
from blockops.utils.vectorize import matMatMul
from blockops.schemes import BlockScheme, register
from blockops.utils.params import setParams, Boolean
    
@register
@setParams(
    collUpdate=Boolean())
class Collocation(BlockScheme):
    """
    Generic class for Collocation methods
    
    Parameters
    ----------
    collUpdate : bool, optional
        Wether to use or not the collocation update at the end of the step.
    """
    def __init__(self, nPoints, ptsType='LEGENDRE', quadType='LOBATTO', form='Z2N',
                 collUpdate=False):
        self.initialize(locals())
        
        nNodes = nPoints-1 if collUpdate else nPoints
        super().__init__(nNodes, ptsType, quadType, form)
        
        if collUpdate:
            self.points = np.append(self.points, [1])
            
            
    def getBlockMatrices(self, lamDt):
        # Main parameters
        collUpdate = self.PARAMS['collUpdate'].value
        form = self.PARAMS['form'].value
        nPoints = self.nPoints
        points = self.points
        
        nNodes = nPoints-1 if collUpdate else nPoints
        nodes = points[:-1] if collUpdate else points
        
        # Compute Q matrix
        polyApprox = LagrangeApproximation(nodes)
        Q = polyApprox.getIntegrationMatrix([(0, tau) for tau in nodes])
        Q = Q[..., None]

        if collUpdate:
            # Use collocation update
            weights = polyApprox.getIntegrationMatrix([(0, 1)]).ravel()
            weights = weights[:, None]
            phi = np.zeros((nNodes+1, nNodes+1, lamDt.size))*lamDt
            phi[:-1, :-1] = np.eye(nNodes)[..., None] - lamDt*Q
            phi[-1, :-1] = -lamDt*weights
            phi[-1, -1] = 1
            chi = np.zeros((nNodes+1, nNodes+1))
            chi[:, -1] = 1
            chi = chi[..., None]
        else:
            # Use interpolation matrix
            phi = np.eye(nNodes)[..., None] - lamDt*Q
            chi = polyApprox.getInterpolationMatrix([1]).repeat(nNodes, axis=0)
            chi = chi[..., None]

        # Eventually switch to node-to-node formulation
        if form == 'N2N':
            T = np.eye(phi.shape[0])
            T[1:,:-1][np.diag_indices(nPoints-1)] = -1
            phi = matMatMul(T, phi)
            chi = matMatMul(T, chi)
            
        return phi, chi
            
    def getBlockCosts(self):
        # TODO : estimation for collocation methods
        return 1, 0
        

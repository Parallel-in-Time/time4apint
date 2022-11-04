#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 13:34:34 2022

@author: cpf5546
"""
import numpy as np

from .poly import NodesGenerator, LagrangeApproximation

STABILITY_FUNCTION_RK = {
    'BE': lambda z: (1-z)**(-1),
    'FE': lambda z: 1+z,
    'TRAP': lambda z: (1+z/2)/(1-z/2),
    'RK2': lambda z: 1+z+z**2/2,
    'RK4': lambda z: 1+z+z**2/2+z**3/6+z**4/24,
    'EXACT': lambda z: np.exp(z)}
RK_METHODS = STABILITY_FUNCTION_RK.keys()


def getBlockMatrices(lamDt, M, scheme, form=None, **kwargs):

    # Reduce M for collocation with exact end-point prolongation
    exactProlong = kwargs.get('exactProlong', False)
    if exactProlong and scheme == 'COLLOCATION':
        M -= 1

    # Time-points for the block discretization
    nodes = kwargs.get('nodes',
                       'LEGENDRE' if scheme=='COLLOCATION' else 'EQUID')
    if isinstance(nodes, str):
        qType = kwargs.get('qType', 'RADAU-RIGHT')
        nodes = NodesGenerator(nodes, qType).getNodes(M)
        nodes += 1
        nodes /= 2
    nodes = np.around(np.ravel(nodes), 14)
    if not ((min(nodes) >= 0) and (max(nodes) <= 1)):
        raise ValueError(f'inconsistent nodes : {nodes}')
    M = len(nodes)
    deltas = np.array(
        [tauR-tauL for tauL, tauR in zip([0]+list(nodes)[:-1], list(nodes))])

    # Node formulation
    if form is None:
        form = 'Z2N' if scheme == 'COLLOCATION' else 'N2N'
    if form not in ['Z2N', 'N2N']:
        raise ValueError('form argument can only be '
                         'N2N (node-to-node) or Z2N (zero-to-node), '
                         f'got {form}')

    # Runge-Kutta types methods
    if scheme in RK_METHODS:

        # Default node-to-node formulation
        nStepPerNode = kwargs.get('nStepPerNode', 1)

        # Compute amplification factor
        z = lamDt*deltas/nStepPerNode
        R = STABILITY_FUNCTION_RK[scheme](z)**(-nStepPerNode)

        # Build phi and chi matrices
        phi = np.diag(R)
        phi[1:,:-1][np.diag_indices(M-1)] = -1
        chi = np.zeros((M, M))
        chi[0, -1] = 1

        # Eventually switch to zero-to-node formulation
        if form == 'Z2N':
            T = np.tril(np.ones((M, M)))
            phi = T @ phi
            chi = T @ chi

    # Collocation methods
    elif scheme == 'COLLOCATION':

        # Default zero-to-node formulation
        polyApprox = LagrangeApproximation(nodes)
        Q = polyApprox.getIntegrationMatrix([(0, tau) for tau in nodes])

        if exactProlong:
            # Using exact prolongation
            nodes = np.array(nodes.tolist()+[1])
            weights = polyApprox.getIntegrationMatrix([(0, 1)]).ravel()
            phi = np.zeros((M+1, M+1))*lamDt
            phi[:-1, :-1] = np.eye(M) - lamDt*Q
            phi[-1, :-1] = -lamDt*weights
            phi[-1, -1] = 1
            chi = np.zeros((M+1, M+1))
            chi[:, -1] = 1
        else:
            phi = np.eye(M) - lamDt*Q
            chi = polyApprox.getInterpolationMatrix([1]).repeat(M, axis=0)

        # Eventually switch to node-to-node formulation
        if form == 'N2N':
            T = np.eye(M)
            T[1:,:-1][np.diag_indices(M-1)] = -1
            phi = T @ phi
            chi = T @ chi

    elif scheme == 'MULTISTEP':  # Adams-Bashforth method

        # Default node-to-node formulation
        a = (1+3/2*lamDt*deltas)
        b = -lamDt/2*deltas

        phi = np.eye(M) + 0*lamDt
        phi[1:,:-1][np.diag_indices(M-1)] = -a[1:]
        phi[2:,:-2][np.diag_indices(M-2)] = -b[2:]

        chi = np.zeros((M, M)) + 0*lamDt
        chi[0, -1] = a[0]
        chi[0, -2] = b[0]
        chi[1, -1] = b[1]

        # Eventually switch to zero-to-node formulation
        if form == 'Z2N':
            T = np.tril(np.ones((M, M)))
            phi = T @ phi
            chi = T @ chi

    else:
        raise NotImplementedError(f'scheme = {scheme}')

    return phi, chi, nodes


def getTransferMatrices(nodesFine, nodesCoarse):
    # Build polynomial approximations
    polyApproxFine = LagrangeApproximation(nodesFine)
    polyApproxCoarse = LagrangeApproximation(nodesCoarse)
    # Compute interpolation matrix
    TFtoC = polyApproxFine.getInterpolationMatrix(nodesCoarse)
    TCtoF = polyApproxCoarse.getInterpolationMatrix(nodesFine)
    return TFtoC, TCtoF

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 13:34:34 2022

@author: cpf5546
"""
import numpy as np

from .poly import NodesGenerator, LagrangeApproximation
from .vectorize import matMatMul


STABILITY_FUNCTION_RK = {
    'BE': lambda z: (1-z)**(-1),
    'FE': lambda z: 1+z,
    'TRAP': lambda z: (1+z/2)/(1-z/2),
    'RK2': lambda z: 1+z+z**2/2,
    'RK4': lambda z: 1+z+z**2/2+z**3/6+z**4/24,
    'EXACT': lambda z: np.exp(z)}
RK_METHODS = STABILITY_FUNCTION_RK.keys()


def getBlockMatrices(lamDt, M, scheme, form=None, **kwargs):

    # Eventually generate matrices for several lamDt
    lamDt = np.ravel(lamDt)[None, :]

    # Reduce M for collocation with exact end-point prolongation
    quadProlong = kwargs.pop('quadProlong', False)
    if quadProlong and scheme == 'COLLOCATION':
        M -= 1

    # Time-points for the block discretization
    points = kwargs.pop('points',
                       'LEGENDRE' if scheme=='COLLOCATION' else 'EQUID')
    if isinstance(points, str):
        quadType = kwargs.pop('quadType', 'RADAU-RIGHT')
        points = NodesGenerator(points, quadType).getNodes(M)
        points += 1
        points /= 2
    points = np.around(np.ravel(points), 14)
    if not ((min(points) >= 0) and (max(points) <= 1)):
        raise ValueError(f'inconsistent time points : {points}')
    M = len(points)
    deltas = np.array(
        [tauR-tauL for tauL, tauR in zip([0]+list(points)[:-1], list(points))])
    deltas = deltas[:, None]

    # Node formulation : node-to-node (N2N) or zero-to-nodes (Z2N)
    if form is None:
        form = 'Z2N' if scheme == 'COLLOCATION' else 'N2N'
    if form not in ['Z2N', 'N2N']:
        raise ValueError('form argument can only be '
                         'N2N (node-to-node) or Z2N (zero-to-node), '
                         f'got {form}')

    # Runge-Kutta types methods
    if scheme in RK_METHODS:

        # Default node-to-node formulation
        nStepsPerPoint = kwargs.pop('nStepsPerPoint', 1)

        # Compute amplification factor
        z = lamDt*deltas/nStepsPerPoint
        R = STABILITY_FUNCTION_RK[scheme](z)**(-nStepsPerPoint)

        # Build phi and chi matrices
        phi = np.zeros_like(R, shape=(M,)+R.shape)
        phi[np.diag_indices(M)] = R
        phi[1:,:-1][np.diag_indices(M-1)] = -1
        chi = np.zeros_like(R, shape=(M, M))
        chi[0, -1] = 1
        chi = chi[..., None]

        # Eventually switch to zero-to-node formulation
        if form == 'Z2N':
            T = np.tril(np.ones((M, M)))
            phi = matMatMul(T, phi)
            chi = matMatMul(T, chi)

        cost = nStepsPerPoint * M

    # Collocation methods
    elif scheme == 'COLLOCATION':

        # Default zero-to-node formulation
        polyApprox = LagrangeApproximation(points)
        Q = polyApprox.getIntegrationMatrix([(0, tau) for tau in points])
        Q = Q[..., None]

        if quadProlong:
            # Using exact prolongation
            points = np.append(points, [1])
            weights = polyApprox.getIntegrationMatrix([(0, 1)]).ravel()
            weights = weights[:, None]
            phi = np.zeros((M+1, M+1, lamDt.size))*lamDt
            phi[:-1, :-1] = np.eye(M)[..., None] - lamDt*Q
            phi[-1, :-1] = -lamDt*weights
            phi[-1, -1] = 1
            chi = np.zeros((M+1, M+1))
            chi[:, -1] = 1
            chi = chi[..., None]
        else:
            phi = np.eye(M)[..., None] - lamDt*Q
            chi = polyApprox.getInterpolationMatrix([1]).repeat(M, axis=0)
            chi = chi[..., None]

        # Eventually switch to node-to-node formulation
        if form == 'N2N':
            T = np.eye(phi.shape[0])
            T[1:,:-1][np.diag_indices(M-1)] = -1
            phi = matMatMul(T, phi)
            chi = matMatMul(T, chi)

        # TODO : specific cost for collocation methods
        cost = 1

    elif scheme == 'MULTISTEP':  # Adams-Bashforth method

        raise NotImplementedError('Multistep scheme not vectorized yet ...')

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

        # TODO : specific cost for multistep methods
        cost = 1

    else:
        raise NotImplementedError(f'scheme = {scheme}')

    # Print warning for unused parameters
    for key, val in kwargs.items():
        print(f'WARNING : {key} ({val}) was given to getBlockMatrices'
              ' but not used')

    # Transpose and eventually squeeze
    phi = phi.transpose((2,0,1))
    chi = chi.transpose((2,0,1))
    if lamDt.size == 1:
        phi = phi.squeeze(axis=0)
        chi = chi.squeeze(axis=0)

    return phi, chi, points, cost, form


def getTransferMatrices(nodesFine, nodesCoarse):
    # Build polynomial approximations
    polyApproxFine = LagrangeApproximation(nodesFine)
    polyApproxCoarse = LagrangeApproximation(nodesCoarse)
    # Compute interpolation matrix
    TFtoC = polyApproxFine.getInterpolationMatrix(nodesCoarse)
    TCtoF = polyApproxCoarse.getInterpolationMatrix(nodesFine)
    return TFtoC, TCtoF

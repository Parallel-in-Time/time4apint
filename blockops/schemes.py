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

RK_METHODS = STABILITY_FUNCTION_RK.keys()


def getBlockMatrices(lamDt, nPoints, scheme, **kwargs):

    # To store and return method and points parameters
    params = {'scheme': scheme}
    paramsPoints = {}

    # Eventually generate matrices for several lamDt
    lamDt = np.ravel(lamDt)[None, :]

    # Reduce M for collocation with integral end-point prolongation
    quadProlong = kwargs.pop('quadProlong', False)
    if quadProlong and scheme == 'COLLOCATION':
        nPoints -= 1
        params['quadProlong'] = quadProlong

    # Time-points for the block discretization
    points = kwargs.pop('points',
                       'LEGENDRE' if scheme=='COLLOCATION' else 'EQUID')
    quadType = kwargs.pop('quadType', 'RADAU-RIGHT')
    if isinstance(points, str):
        paramsPoints = {'quadType': quadType}
        paramsPoints['points'] = points
        points = NodesGenerator(points, quadType).getNodes(nPoints)
        points += 1
        points /= 2
    else:
        paramsPoints['points'] = 'USER'
    points = np.around(np.ravel(points), 14)
    if not ((min(points) >= 0) and (max(points) <= 1)):
        raise ValueError(f'inconsistent time points : {points}')
    nPoints = len(points)
    deltas = np.array(
        [tauR-tauL for tauL, tauR in zip([0]+list(points)[:-1], list(points))])
    deltas = deltas[:, None]

    # Node formulation : zero-to-nodes (Z2N, default) or node-to-node (N2N)
    form = kwargs.pop('form', 'Z2N')
    if form not in ['Z2N', 'N2N']:
        raise ValueError('form argument can only be '
                         'N2N (node-to-node) or Z2N (zero-to-node), '
                         f'got {form}')
    params['form'] = form

    # Runge-Kutta types methods
    if scheme in RK_METHODS:

        # Default node-to-node formulation
        nStepsPerPoint = kwargs.pop('nStepsPerPoint', 1)
        params['nStepsPerPoint'] = nStepsPerPoint

        # Compute amplification factor
        z = lamDt*deltas/nStepsPerPoint
        R = STABILITY_FUNCTION_RK[scheme](z)**(-nStepsPerPoint)

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

        cost = nStepsPerPoint * nPoints

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
            phi = np.zeros((nPoints+1, nPoints+1, lamDt.size))*lamDt
            phi[:-1, :-1] = np.eye(nPoints)[..., None] - lamDt*Q
            phi[-1, :-1] = -lamDt*weights
            phi[-1, -1] = 1
            chi = np.zeros((nPoints+1, nPoints+1))
            chi[:, -1] = 1
            chi = chi[..., None]
        else:
            phi = np.eye(nPoints)[..., None] - lamDt*Q
            chi = polyApprox.getInterpolationMatrix([1]).repeat(nPoints, axis=0)
            chi = chi[..., None]

        # Eventually switch to node-to-node formulation
        if form == 'N2N':
            T = np.eye(phi.shape[0])
            T[1:,:-1][np.diag_indices(nPoints-1)] = -1
            phi = matMatMul(T, phi)
            chi = matMatMul(T, chi)

        # TODO : specific cost for collocation methods
        cost = 1

    elif scheme == 'MULTISTEP':  # Adams-Bashforth method

        raise NotImplementedError('Multistep scheme not vectorized yet ...')

        # Default node-to-node formulation
        a = (1+3/2*lamDt*deltas)
        b = -lamDt/2*deltas

        phi = np.eye(nPoints) + 0*lamDt
        phi[1:,:-1][np.diag_indices(nPoints-1)] = -a[1:]
        phi[2:,:-2][np.diag_indices(nPoints-2)] = -b[2:]

        chi = np.zeros((nPoints, nPoints)) + 0*lamDt
        chi[0, -1] = a[0]
        chi[0, -2] = b[0]
        chi[1, -1] = b[1]

        # Eventually switch to zero-to-node formulation
        if form == 'Z2N':
            T = np.tril(np.ones((nPoints, nPoints)))
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

    return phi, chi, points, cost, params, paramsPoints


def getTransferMatrices(nodesFine, nodesCoarse):
    # Build polynomial approximations
    polyApproxFine = LagrangeApproximation(nodesFine)
    polyApproxCoarse = LagrangeApproximation(nodesCoarse)
    # Compute interpolation matrix
    TFtoC = polyApproxFine.getInterpolationMatrix(nodesCoarse)
    TCtoF = polyApproxCoarse.getInterpolationMatrix(nodesFine)
    return TFtoC, TCtoF

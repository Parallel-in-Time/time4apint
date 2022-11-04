#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 13:47:39 2022

Standalone module to generate quadrature points and Lagrange interpolant
polynomials for interpolation and integration.

@author: cpf5546
"""
import numpy as np
from scipy.special import roots_legendre
from scipy.linalg import eigh_tridiagonal

NODE_TYPES = ['EQUID', 'LEGENDRE',
              'CHEBY-1', 'CHEBY-2', 'CHEBY-3', 'CHEBY-4']

QUAD_TYPES = ['GAUSS', 'RADAU-LEFT', 'RADAU-RIGHT', 'LOBATTO']


class NodesError(Exception):
    """Exception class to handle error in NodesGenerator class"""
    pass


class NodesGenerator(object):
    """
    Class that can be used to generate generic distribution of nodes derived
    from Gauss quadrature rule.
    Its implementation is fully inspired from a book of W. Gautschi [1]_.

    Attributes
    ----------
    node_type : str
        The type of node distribution
    quad_type : str
        The quadrature type

    Methods
    -------
    __init__(self, node_type='LEGENDRE', quad_type='LOBATTO')
        Instanciate the NodesGenerator object.
    getNodes(self, num_nodes)
        Computes a given number of quadrature nodes.
    getOrthogPolyCoefficients(self, num_coeff)
        Produces a given number of analytic three-term recurrence coefficients.
    evalOrthogPoly(self, t, alpha, beta)
        Evaluates the two higher order orthogonal polynomials corresponding
        to the given (alpha,beta) coefficients.
    getTridiagCoefficients(self, num_nodes)
        Computes recurrence coefficients for the tridiagonal Jacobian matrix,
        taking into account the quadrature type.

    .. [1] W. Gautschi, "Orthogonal polynomials: computation and approximation."
       OUP Oxford, 2004.
    """

    def __init__(self, node_type='LEGENDRE', quad_type='LOBATTO'):
        """

        Parameters
        ----------
        node_type : str, optional
            The type of node distribution, can be

            - EQUID : equidistant nodes
            - LEGENDRE : node distribution from Legendre polynomials
            - CHEBY-1 : node distribution from Chebychev polynomials (1st kind)
            - CHEBY-2 : node distribution from Chebychev polynomials (2nd kind)
            - CHEBY-3 : node distribution from Chebychev polynomials (3rd kind)
            - CHEBY-4 : node distribution from Chebychev polynomials (4th kind)

            The default is 'LEGENDRE'.

        quad_type : str, optional
            The quadrature type, can be

            - GAUSS : inner point only, no node at boundary
            - RADAU-LEFT : only left boundary as node
            - RADAU-RIGHT : only right boundary as node
            - LOBATTO : left and right boundary as node

            The default is 'LOBATTO'.
        """

        # Check argument validity
        for arg, vals in zip(['node_type', 'quad_type'],
                             [NODE_TYPES, QUAD_TYPES]):
            val = eval(arg)
            if val not in vals:
                raise NodesError(
                    f"{arg}='{val}' not implemented, must be in {vals}")

        # Store attributes
        self.node_type = node_type
        self.quad_type = quad_type

    def getNodes(self, num_nodes):
        """
        Computes a given number of quadrature nodes.

        Parameters
        ----------
        num_nodes : int
            Number of nodes to compute.

        Returns
        -------
        nodes : np.1darray
            Nodes located in [-1, 1], in increasing order.
        """
        # Check number of nodes
        if self.quad_type in ['LOBATTO', 'RADAU-LEFT'] and num_nodes < 2:
            raise NodesError(
                f"num_nodes must be larger than 2 for {self.quad_type}, "
                f"but for {num_nodes}")
        elif num_nodes < 1:
            raise NodesError("you surely want at least one node ;)")

        # Equidistant nodes
        if self.node_type == 'EQUID':
            if self.quad_type == 'GAUSS':
                return np.linspace(-1, 1, num=num_nodes + 2)[1:-1]
            elif self.quad_type == 'LOBATTO':
                return np.linspace(-1, 1, num=num_nodes)
            elif self.quad_type == 'RADAU-RIGHT':
                return np.linspace(-1, 1, num=num_nodes + 1)[1:]
            elif self.quad_type == 'RADAU-LEFT':
                return np.linspace(-1, 1, num=num_nodes + 1)[:-1]

        # Quadrature nodes linked to orthogonal polynomials
        alpha, beta = self.getTridiagCoefficients(num_nodes)
        nodes = eigh_tridiagonal(alpha, np.sqrt(beta[1:]))[0]
        nodes.sort()

        return nodes

    def getOrthogPolyCoefficients(self, num_coeff):
        """
        Produces a given number of analytic three-term recurrence coefficients.

        Parameters
        ----------
        num_coeff : int
            Number of coefficients to compute.

        Returns
        -------
        alpha : np.1darray
            The alpha coefficients of the three-term recurrence.
        beta : np.1darray
            The beta coefficients of the three-term recurrence.
        """
        if self.node_type == 'LEGENDRE':
            k = np.arange(num_coeff, dtype=float)
            alpha = 0 * k
            beta = k**2 / (4 * k**2 - 1)
            beta[0] = 2
        elif self.node_type == 'CHEBY-1':
            alpha = np.zeros(num_coeff)
            beta = np.full(num_coeff, 0.25)
            beta[0] = np.pi
            if num_coeff > 1:
                beta[1] = 0.5
        elif self.node_type == 'CHEBY-2':
            alpha = np.zeros(num_coeff)
            beta = np.full(num_coeff, 0.25)
            beta[0] = np.pi / 2
        elif self.node_type == 'CHEBY-3':
            alpha = np.zeros(num_coeff)
            alpha[0] = 0.5
            beta = np.full(num_coeff, 0.25)
            beta[0] = np.pi
        elif self.node_type == 'CHEBY-4':
            alpha = np.zeros(num_coeff)
            alpha[0] = -0.5
            beta = np.full(num_coeff, 0.25)
            beta[0] = np.pi
        return alpha, beta

    def evalOrthogPoly(self, t, alpha, beta):
        """
        Evaluates the two higher order orthogonal polynomials corresponding
        to the given (alpha,beta) coefficients.

        Parameters
        ----------
        t : float or np.1darray
            The point where to evaluate the orthogonal polynomials.
        alpha : np.1darray
            The alpha coefficients of the three-term recurrence.
        beta : np.1darray
            The beta coefficients of the three-term recurrence.

        Returns
        -------
        pi[0] : float or np.1darray
            The second higher order orthogonal polynomial evaluation.
        pi[1] : float or np.1darray
            The higher oder orthogonal polynomial evaluation.
        """
        t = np.asarray(t, dtype=float)
        pi = np.array([np.zeros_like(t) for i in range(3)])
        pi[1:] += 1
        for alpha_j, beta_j in zip(alpha, beta):
            pi[2] *= (t - alpha_j)
            pi[0] *= beta_j
            pi[2] -= pi[0]
            pi[0] = pi[1]
            pi[1] = pi[2]
        return pi[0], pi[1]

    def getTridiagCoefficients(self, num_nodes):
        """
        Computes recurrence coefficients for the tridiagonal Jacobian matrix,
        taking into account the quadrature type.

        Parameters
        ----------
        num_nodes : int
            Number of nodes that should be computed from those coefficients.

        Returns
        -------
        alpha : np.1darray
            The modified alpha coefficients of the three-term recurrence.
        beta : np.1darray
            The modified beta coefficients of the three-term recurrence.
        """
        # Coefficients for Gauss quadrature type
        alpha, beta = self.getOrthogPolyCoefficients(num_nodes)

        # If not Gauss quadrature type, modify the alpha/beta coefficients
        if self.quad_type.startswith('RADAU'):
            b = -1. if self.quad_type.endswith('LEFT') else 1.
            b1, b2 = self.evalOrthogPoly(b, alpha[:-1], beta[:-1])[:2]
            alpha[-1] = b - beta[-1] * b1 / b2
        elif self.quad_type == 'LOBATTO':
            a, b = -1., 1.
            a2, a1 = self.evalOrthogPoly(a, alpha[:-1], beta[:-1])[:2]
            b2, b1 = self.evalOrthogPoly(b, alpha[:-1], beta[:-1])[:2]
            alpha[-1], beta[-1] = np.linalg.solve(
                [[a1, a2],
                 [b1, b2]],
                [a * a1, b * b1])
        return alpha, beta


def computeFejerRule(n):
    """
    Compute a Fejer rule of the first kind, using DFT (Waldvogel 2006)
    Inspired from quadpy (https://github.com/nschloe/quadpy @Nico_Schlömer)

    Parameters
    ----------
    n : int
        Number of points for the quadrature rule.

    Returns
    -------
    nodes : np.1darray(n)
        The nodes of the quadrature rule
    weights : np.1darray(n)
        The weights of the quadrature rule.
    """
    # Initialize output variables
    n = int(n)
    nodes = np.empty(n, dtype=float)
    weights = np.empty(n, dtype=float)

    # Compute nodes
    theta = np.arange(1, n + 1, dtype=float)[-1::-1]
    theta *= 2
    theta -= 1
    theta *= np.pi / (2 * n)
    np.cos(theta, out=nodes)

    # Compute weights
    # -- Initial variables
    N = np.arange(1, n, 2)
    lN = len(N)
    m = n - lN
    K = np.arange(m)
    # -- Build v0
    v0 = np.concatenate([
        2 * np.exp(1j * np.pi * K / n) / (1 - 4 * K**2),
        np.zeros(lN + 1)])
    # -- Build v1 from v0
    v1 = np.empty(len(v0) - 1, dtype=complex)
    np.conjugate(v0[:0:-1], out=v1)
    v1 += v0[:-1]
    # -- Compute inverse fourier transform
    w = np.fft.ifft(v1)
    if max(w.imag) > 1.0e-15:
        raise ValueError(
            f'Max imaginary value to important for ifft: {max(w.imag)}')
    # -- Store weights
    weights[:] = w.real

    return nodes, weights


class LagrangeApproximation(object):
    r"""
    Class approximating any function on a given set of points using barycentric
    Lagrange interpolation.

    Let note :math:`(t_j)_{0\leq j<n}` the set of points, then any scalar
    function :math:`f` can be approximated by the barycentric formula :

    .. math::
        p(x) =
        \frac{\displaystyle \sum_{j=0}^{n-1}\frac{w_j}{x-x_j}f_j}
        {\displaystyle \sum_{j=0}^{n-1}\frac{w_j}{x-x_j}},

    where :math:`f_j=f(t_j)` and

    .. math::
        w_j = \frac{1}{\prod_{k\neq j}(x_j-x_k)}

    are the barycentric weights.
    The theory and implementation is inspired from [1]_.

    Attributes
    ----------
    points : np.1darray
        The interpolating points
    weights : np.1darray
        The associated barycentric weights
    n : int (property)
        The number of points

    Methods
    -------
    __init__(self, points, weightComputation='AUTO', scaleRef='MAX')
        Instanciate the LagrangeApproximation object.
    getInterpolationMatrix(self, times):
        Compute the interpolation matrix for a given set of discrete "time" points.
    getIntegrationMatrix(self, intervals, numQuad='LEGENDRE_NUMPY')
        Compute the integration matrix for a given set of intervals.

    .. [1] Berrut, J. P., & Trefethen, L. N. (2004).
           "Barycentric lagrange interpolation." SIAM review, 46(3), 501-517.
    """

    def __init__(self, points, weightComputation='AUTO', scaleRef='MAX'):
        """

        Parameters
        ----------
        points : list, tuple or np.1darray
            The given interpolation points, no specific scaling, but must be
            ordered in increasing order.
        weightComputation : str, optional
            Algorithm used to compute the barycentric weights. Can be :

            - 'FAST' : uses the analytic formula (unstable for large number of points)
            - 'STABLE' : uses logarithmic difference and scaling of the weights
            - 'CHEBFUN' : uses the same approach as in the chebfun package

            The default is 'AUTO' : it tries the 'FAST' algorithm, and if an
            overflow is detected, it switches to the 'STABLE' algorithm.
        scaleRef : str, optional
            Scaling used in the 'STABLE' algorithm for weight computation.
            Can be :

            - 'ZERO' : scaling based on the weight for the value closest to :math:`t=0`.
            - 'MAX' : scaling based on the maximum weight value.

            The default is 'MAX'.
        """
        points = np.asarray(points).ravel()

        diffs = points[:, None] - points[None, :]
        diffs[np.diag_indices_from(diffs)] = 1

        def analytic(diffs):
            # Fast implementation (unstable for large number of points)
            invProd = np.prod(diffs, axis=1)
            invProd **= -1
            return invProd

        def logScale(diffs):
            # Implementation using logarithmic difference and scaling
            sign = np.sign(diffs).prod(axis=1)
            wLog = -np.log(np.abs(diffs)).sum(axis=1)
            if scaleRef == 'ZERO':
                wScale = wLog[np.argmin(np.abs(points))]
            elif scaleRef == 'MAX':
                wScale = wLog.max()
            else:
                raise NotImplementedError(f'scaleRef={scaleRef}')
            invProd = np.exp(wLog - wScale)
            invProd *= sign
            return invProd

        def chebfun(diffs):
            # Implementation used in chebfun
            diffs *= 4 / (points.max() - points.min())
            sign = np.sign(diffs).prod(axis=1)
            vv = np.exp(np.log(np.abs(diffs)).sum(axis=1))
            invProd = (sign * vv)
            invProd **= -1
            invProd /= np.linalg.norm(invProd, np.inf)
            return invProd

        if weightComputation == 'AUTO':
            with np.errstate(divide='raise', over='ignore'):
                try:
                    invProd = analytic(diffs)
                except FloatingPointError:
                    invProd = logScale(diffs)
        elif weightComputation == 'FAST':
            invProd = analytic(diffs)
        elif weightComputation == 'STABLE':
            invProd = logScale(diffs)
        elif weightComputation == 'CHEBFUN':
            invProd = chebfun(diffs)
        else:
            raise NotImplementedError(
                f'weightComputation={weightComputation}')
        weights = invProd

        # Store attributes
        self.points = points
        self.weights = weights
        self.weightComputation = weightComputation

    @property
    def n(self):
        return self.points.size

    def getInterpolationMatrix(self, times):
        r"""
        Compute the interpolation matrix for a given set of discrete "time"
        points.

        For instance, if we note :math:`\vec{f}` the vector containing the
        :math:`f_j=f(t_j)` values, and :math:`(\tau_m)_{0\leq m<M}`
        the "time" points where to interpolate.
        Then :math:`I[\vec{f}]`, the vector containing the interpolated
        :math:`f(\tau_m)` values, can be obtained using :

        .. math::
            I[\vec{f}] = P_{Inter} \vec{f},

        where :math:`P_{Inter}` is the interpolation matrix returned by this
        method.

        Parameters
        ----------
        times : list-like or np.1darray
            The discrete "time" points where to interpolate the function.

        Returns
        -------
        PInter : np.2darray(M, n)
            The interpolation matrix, with :math:`M` rows (size of the **times**
            parameter) and :math:`n` columns.

        """
        # Compute difference between times and Lagrange points
        times = np.asarray(times)
        with np.errstate(divide='ignore'):
            iDiff = 1 / (times[:, None] - self.points[None, :])

        # Find evaluated positions that coincide with one Lagrange point
        concom = (iDiff == np.inf) | (iDiff == -np.inf)
        i, j = np.where(concom)

        # Replace iDiff by on on those lines to get a simple copy of the value
        iDiff[i, :] = concom[i, :]

        # Compute interpolation matrix using weights
        PInter = iDiff * self.weights
        PInter /= PInter.sum(axis=-1)[:, None]

        return PInter

    def getIntegrationMatrix(self, intervals, numQuad='LEGENDRE_NUMPY'):
        r"""
        Compute the integration matrix for a given set of intervals.

        For instance, if we note :math:`\vec{f}` the vector containing the
        :math:`f_j=f(t_j)` values, and
        :math:`(\tau_{m,left}, \tau_{m,right})_{0\leq m<M}` the different
        interval where the function should be integrated using the barycentric
        interpolant polynomial.
        Then :math:`\Delta[\vec{f}]`, the vector containing the approximations
        of

        .. math::
            \int_{\tau_{m,left}}^{\tau_{m,right}} f(t)dt,

        can be obtained using :

        .. math::
            \Delta[\vec{f}] = P_{Integ} \vec{f},

        where :math:`P_{Integ}` is the interpolation matrix returned by this
        method.

        Parameters
        ----------
        intervals : list of pairs
            A list of all integration intervals.
        numQuad : str, optional
            Quadrature rule used to integrate the interpolant barycentric
            polynomial. Can be :

            - 'LEGENDRE_NUMPY' : Gauss-Legendre rule from Numpy
            - 'LEGENDRE_SCIPY' : Gauss-Legendre rule from Scipy
            - 'FEJER' : internaly implemented Fejer-I rule

            The default is 'LEGENDRE_NUMPY'.

        Returns
        -------
        PInter : np.2darray(M, n)
            The integration matrix, with :math:`M` rows (number of intervals)
            and :math:`n` columns.
        """
        if numQuad == 'LEGENDRE_NUMPY':
            # Legendre gauss rule, integrate exactly polynomials of deg. (2n-1)
            iNodes, iWeights = np.polynomial.legendre.leggauss((self.n + 1) // 2)
        elif numQuad == 'LEGENDRE_SCIPY':
            # Using Legendre scipy implementation
            iNodes, iWeights = roots_legendre((self.n + 1) // 2)
        elif numQuad == 'FEJER':
            # Fejer-I rule, integrate exactly polynomial of deg. n-1
            iNodes, iWeights = computeFejerRule(self.n - ((self.n + 1) % 2))
        else:
            raise NotImplementedError(f'numQuad={numQuad}')

        # Compute quadrature nodes for each interval
        intervals = np.array(intervals)
        aj, bj = intervals[:, 0][:, None], intervals[:, 1][:, None]
        tau, omega = iNodes[None, :], iWeights[None, :]
        tEval = (bj - aj) / 2 * tau + (bj + aj) / 2

        # Compute the integrand function on nodes
        integrand = self.getInterpolationMatrix(tEval.ravel()).T.reshape(
            (-1,) + tEval.shape)

        # Apply quadrature rule to integrate
        integrand *= omega
        integrand *= (bj - aj) / 2
        PInter = integrand.sum(axis=-1).T

        return PInter

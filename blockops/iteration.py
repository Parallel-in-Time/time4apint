#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 15:40:41 2022

@author: cpf5546
"""
import numpy as np
import sympy as sy

from .block import BlockOperator, one
from .run import PintRun
from .utils import getCoeffsFromFormula


# -----------------------------------------------------------------------------
# Base class
# -----------------------------------------------------------------------------
class BlockIteration(object):
    """DOCTODO"""

    def __init__(self, update, predictor='', rules=None, name=None, **blockOps):
        """
        DOCTODO

        Parameters
        ----------
        update : TYPE
            DESCRIPTION.
        predictor : TYPE
            DESCRIPTION.
        rules : TYPE, optional
            DESCRIPTION. The default is None.
        **blockOps : TYPE
            DESCRIPTION.
        """
        # Store name for the block iteration (optional)
        self.name = name

        # Store block coefficients from the iteration update formula
        self.blockCoeffs = getCoeffsFromFormula(update, blockOps)

        # Store block coefficients from the predictor formula
        self.predBlockCoeffs = getCoeffsFromFormula(predictor, blockOps)

        # Stores the generated symbols for the rules
        # TODO : check if the rules hold with the given matrices
        rules = [] if rules is None else rules

        def condEval(x):
            if isinstance(x, BlockOperator):
                return x.symbol
            else:
                e = eval(x, blockOps)
                if hasattr(e, 'symbol'):
                    return e.symbol
                else:
                    return e

        self.rules = {condEval(a): condEval(b) for a, b in rules}

        # Attribute that can be used to store an associated problem
        self.problem = None

        # Saving the BlockOps to make it easier to get the cost later on
        self.blockOps = {v.name: v for k, v in blockOps.items() if isinstance(v, BlockOperator)}

        self.update = update
        self.predictor = predictor

    @property
    def coeffs(self):
        """Return an iterator on the (key, values) of blockCoeffs"""
        return self.blockCoeffs.items()

    @property
    def predCoeffs(self):
        """Return an iterator on the (key, values) of predBlockCoeffs"""
        return self.predBlockCoeffs.items()

    @property
    def M(self):
        return list(self.blockCoeffs.values())[0].M

    def __call__(self, N, K, u0=None, initSol=False, predSol=None):
        """
        Evaluate the block iteration from given initial solution, number of
        blocks and number of iteration.

        Parameters
        ----------
        N : int
            Number of blocks.
        K : int or N-sequence of int
            Number of iteration, for each block (if int) or each block
            separately.
        u0 : M-sequence of floats or complex
            Initial solution used for numerical evaluation
            (not required if M==0).
        initSol : bool, optional
            Wether or not return the initial solution in the solution array.
            The default is False.
        predSol : N-sequence of vector, optional
            Prediction solution used if the block iteration has no prediction
            rule. The default is None.

        Returns
        -------
        np.array of size (K+1, N or N+1)
            The solution fo each block and each iteration. If initSol==True,
            includes the initial solution u0 and has size (K+1, N+1).
            If not, has size (K+1,N).
        """
        if self.M == 0:

            # Symbolic evaluation
            u0 = sy.symbols('u0', commutative=False)
            u = np.zeros((K + 1, N + 1), dtype=sy.Expr)
            u[:, 0] = u0
            # Prediction
            if len(self.predCoeffs) != 0:
                pred = self.predBlockCoeffs[(0, 0)]
                for n in range(N):
                    u[0, n + 1] = pred.symbol * u[0, n]
            else:
                u[0, 1:] = [sy.symbols(f'u_{n+1}^0', commutative=False)
                            for n in range(N)]
            # Iterations
            for k in range(K):
                for n in range(N):
                    for (nMod, kMod), b in self.coeffs:
                        u[k + 1, n + 1] += b.symbol * u[k + kMod, n + nMod]
                    u[k + 1, n + 1] = u[k + 1, n + 1].simplify()

        else:

            # Numerical evaluation
            if u0 is None:
                raise ValueError(
                    'u0 must be provided for numerical evaluation'
                    ' of a block iteration')
            u0 = np.asarray(u0)
            u = np.zeros((K + 1, N + 1, u0.size), dtype=u0.dtype)
            u[:, 0] = u0
            # Prediction
            if len(self.predCoeffs) != 0:
                pred = self.predBlockCoeffs[(0, 0)]
                for n in range(N):
                    u[0, n + 1] = pred(u[0, n])
            else:
                if predSol is None:
                    raise ValueError(
                        'evaluating block iteration without prediction rule'
                        ' requires predSol list given as argument')
                for n in range(N):
                    u[0, n + 1] = predSol[n]
            # Iterations
            for k in range(K):
                for n in range(N):
                    for (nMod, kMod), blockOp in self.coeffs:
                        u[k + 1, n + 1] += blockOp(u[k + kMod, n + nMod])

        if initSol:
            return u
        else:
            return u[:, 1:]

    def speedup(self, N, K):
        run = PintRun(blockIteration=self, nBlocks=N, kMax=K)
        runtime = run.getMinimalRuntime()

        # TODO: How to get the runtime of time stepping?
        runtime_ts = N * 10

        print('=============================')
        if self.name is None:
            print(f'Block iteration: {self.update}')
        else:
            print(f'Block iteration: {self.name}')
            print(f'Update: {self.update}')
        print(f'Predictor: {self.predictor}')
        print(f'N={N}, K={K}')
        print(f'Theoretical lower runtime bound: {runtime}')
        print(f'Runtime time-stepping: {runtime_ts} (This is currently not the correct value)')
        print(
            f'Theoretical speedup compared to time stepping: {(runtime_ts / runtime):.2f} (This is currently not the correct value)')
        print('=============================')
        return (runtime_ts / runtime)

    def plotGraph(self, N, K):
        run = PintRun(blockIteration=self, nBlocks=N, kMax=K)
        run.plotGraph(self.name)


# -----------------------------------------------------------------------------
# Inherited specialized class
# -----------------------------------------------------------------------------
ALGORITHMS = {}


def register(cls):
    ALGORITHMS[cls.__name__] = cls
    return cls


@register
class Parareal(BlockIteration):

    def __init__(self, implicitForm=True, coarsePred=True, **blockOps):
        if implicitForm:
            B00 = "(phi**(-1)*chi-phiDelta**(-1)*chi) * u_{n}^k"
            B01 = "phiDelta**(-1)*chi * u_{n}^{k+1}"
            predictor = "phiDelta**(-1)*chi*u_{n}^0" if coarsePred else ""
        else:
            B00 = "(F-G) * u_{n}^k"
            B01 = "G * u_{n}^{k+1}"
            predictor = "G * u_{n}^0" if coarsePred else ""
        update = f"{B00} + {B01}"
        super().__init__(update, predictor, rules=None, name='Parareal',
                         **blockOps)


@register
class ABJ(BlockIteration):

    def __init__(self, implicitForm=True, coarsePred=True, **blockOps):
        if implicitForm:
            B00 = "phiDelta**(-1)*chi * u_{n}^k"
            B10 = "(I-phiDelta**-1 * phi) * u_{n+1}^{k}"
            predictor = "phiDelta**(-1)*chi*u_{n}^0" if coarsePred else ""
        else:
            B00 = "G * u_{n}^k"
            B10 = "(I-G*F**(-1)) * u_{n}^{k+1}"
            predictor = "G * u_{n}^0" if coarsePred else ""
        blockOps['I'] = one
        update = f"{B10} + {B00}"
        super().__init__(update, predictor, rules=None, name='ABJ',
                         **blockOps)


@register
class ABGS(BlockIteration):

    def __init__(self, implicitForm=True, coarsePred=True, **blockOps):
        if implicitForm:
            B01 = "phiDelta**(-1)*chi * u_{n}^{k+1}"
            B10 = "(I-phiDelta**-1 * phi) * u_{n+1}^{k}"
            predictor = "phiDelta**(-1)*chi*u_{n}^0" if coarsePred else ""
        else:
            B01 = "G * u_{n}^{k+1}"
            B10 = "(I-G*F**(-1)) * u_{n}^{k+1}"
            predictor = "G * u_{n}^0" if coarsePred else ""
        update = f"{B10} + {B01}"
        blockOps['I'] = one
        super().__init__(update, predictor, rules=None, name='ABGS',
                         **blockOps)

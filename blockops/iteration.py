#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 15:40:41 2022

@author: cpf5546
"""
import numpy as np

from .block import BlockOperator
from .run import PintRun
from .utils import getCoeffsFromFormula


# -----------------------------------------------------------------------------
# Base class
# -----------------------------------------------------------------------------
class BlockIteration(object):
    """DOCTODO"""

    NEW_VERSION = None

    def __init__(self, update, predictor='', rules=None, **blockOps):
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

    def __call__(self, u0, K, N, initSol=False):
        u0 = np.asarray(u0)
        u = np.zeros((K + 1, N + 1, u0.size), dtype=u0.dtype)
        u[:, 0] = u0
        # Prediction
        pred = self.predBlockCoeffs[(0, 0)]
        for n in range(N):
            u[0, n + 1] = pred(u[0, n])
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
        print(f'Block iteration: {self.update}')
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
        run.plotGraph()


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
            B00 = "(phi**(-1)*chi-phiDelta**(-1)*chi) * u_{n}^k "
            B01 = "phiDelta**(-1)*chi * u_{n}^{k+1}"
            predictor = "phiDelta**(-1)*chi*u_{n}^0" if coarsePred else ""
        else:
            B00 = "(F-G) * u_{n}^k "
            B01 = "G * u_{n}^{k+1}"
            predictor = "G * u_{n}^0" if coarsePred else ""
        update = f"{B00} + {B01}"
        super().__init__(update, predictor, rules=None, **blockOps)

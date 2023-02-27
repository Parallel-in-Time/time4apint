#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 15:40:41 2022

@author: cpf5546
"""
import numpy as np
import sympy as sy
from typing import Dict

from .block import BlockOperator, I
from .run import PintRun
from .schedule import getSchedule
from .utils import getCoeffsFromFormula


# -----------------------------------------------------------------------------
# Base class
# -----------------------------------------------------------------------------
class BlockIteration(object):
    """DOCTODO"""

    needApprox = False
    needCoarse = False

    def __init__(self, update, propagator,
                 predictor=None, rules=None, name=None, **blockOps):
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

        # Store block coefficient for the (fine) propagator
        if isinstance(propagator, BlockOperator):
            self.propagator = propagator
        else:
            self.propagator = eval(propagator, blockOps)

        # Store block coefficients from the predictor
        if isinstance(predictor, BlockOperator):
            self.predictor = predictor
        else:
            self.predictor = eval(str(predictor), blockOps)

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

        # Saving the BlockOps to make it easier to get the cost later on
        self.blockOps = {v.name: v for v in blockOps.values()
                         if isinstance(v, BlockOperator)}

        # Saving update formula, just in case ...
        self.update = update

        # Variable to store eventual associated problem
        self.prob = None

    @property
    def coeffs(self):
        """Return an iterator on the (key, values) of blockCoeffs"""
        return self.blockCoeffs.items()

    @property
    def M(self):
        return max(op.M for op in self.blockCoeffs.values())

    @property
    def nLam(self):
        return max(op.nLam for op in self.blockCoeffs.values())

    @property
    def nBlocks(self):
        return np.inf if self.prob is None else self.prob.nBlocks

    @property
    def u0(self):
        return None if self.prob is None else self.prob.u0

    def __call__(self, nIter, nBlocks=None, u0=None, initSol=False, predSol=None):
        """
        Evaluate the block iteration from given initial solution, number of
        blocks and number of iteration.

        Parameters
        ----------
        nIter : int or N-sequence of int
            Number of iteration, for each block (if int) or each block
            separately.
        nBlocks : int, optional
            Number of blocks. The default takes the nBlocks value of the
            associated problem.
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
        np.array of size (nIter+1, nBlocks or nBlocks+1)
            The solution fo each block and each iteration. If initSol==True,
            includes the initial solution u0 and has size (nIter+1, nBlocks+1).
            If not, has size (nIter+1, nBlocks).
        """
        nBlocks = self.nBlocks if nBlocks is None else nBlocks
        if nBlocks == np.inf:
            raise ValueError('need to specify a number of blocks somehow')

        if self.M == 0:

            # Symbolic evaluation
            u0 = sy.symbols('u0', commutative=False)
            u = np.zeros((nIter + 1, nBlocks + 1), dtype=sy.Expr)
            u[:, 0] = u0
            # Prediction
            if len(self.predCoeffs) != 0:
                pred = self.predictor
                for n in range(nBlocks):
                    u[0, n + 1] = pred.symbol * u[0, n]
            else:
                u[0, 1:] = [sy.symbols(f'u_{n + 1}^0', commutative=False)
                            for n in range(nBlocks)]
            # Iterations
            for k in range(nIter):
                for n in range(nBlocks):
                    for (nMod, kMod), b in self.coeffs:
                        u[k + 1, n + 1] += b.symbol * u[k + kMod, n + nMod]
                    u[k + 1, n + 1] = u[k + 1, n + 1].simplify()

        else:

            # Numerical evaluation
            u0 = self.u0 if u0 is None else u0
            if u0 is None:
                raise ValueError(
                    'u0 must be provided for numerical evaluation'
                    ' of a block iteration')

            u0 = np.asarray(u0)
            if self.nLam > 1:
                u = np.zeros((nIter + 1, nBlocks + 1, self.nLam, self.M), dtype=u0.dtype)
            else:
                u = np.zeros((nIter + 1, nBlocks + 1, self.M), dtype=u0.dtype)
            u[:, 0] = u0
            # Prediction
            if self.predictor is not None:
                for n in range(nBlocks):
                    u[0, n + 1] = self.predictor(u[0, n])
            else:
                if predSol is None:
                    raise ValueError(
                        'evaluating block iteration without prediction rule'
                        ' requires predSol list given as argument')
                for n in range(nBlocks):
                    u[0, n + 1] = predSol[n]
            # Iterations
            for k in range(nIter):
                for n in range(nBlocks):
                    for (nMod, kMod), blockOp in self.coeffs:
                        u[k + 1, n + 1] += blockOp(u[k + kMod, n + nMod])

        if initSol:
            return u
        else:
            return u[:, 1:]

    def getRuntime(self, N, K, nProc, schedule_type='BLOCK-BY-BLOCK'):
        K = self.checkK(N=N, K=K)
        run = PintRun(blockIteration=self, nBlocks=N, kMax=K)
        schedule = getSchedule(taskPool=run.taskPool, nProc=nProc, nPoints=N + 1, schedule_type=schedule_type)
        return schedule.getRuntime()

    def getPerformances(
            self, N, K, nProc=None, schedule_type='BLOCK-BY-BLOCK', verbose=False):

        seqPropCost = self.propagator.cost
        if (seqPropCost is None) or (seqPropCost == 0):
            raise ValueError(
                'no cost given for fine propagator,'
                ' cannot measure performances')
        runtime_ts = seqPropCost * N

        K = self.checkK(N=N, K=K)
        print(f' -- computing {schedule_type} cost for K={K}')

        run = PintRun(blockIteration=self, nBlocks=N, kMax=K)
        schedule = getSchedule(
            taskPool=run.taskPool, nProc=nProc, nPoints=N + 1,
            schedule_type=schedule_type)
        runtime = schedule.getRuntime()
        nProc = schedule.nProc

        if verbose:
            optimal_runtime = run.pintGraph.longestPath()
            print('=============================')
            if self.name is None:
                print(f'Block iteration: {self.update}')
            else:
                print(f'Block iteration: {self.name}')
                print(f'Update: {self.update}')
            print(f'Predictor: {self.predictor}')
            print(f'N={N}, K={K} \n')
            print(f'Runtime of schedule={schedule.NAME} for nProc={nProc}: {runtime}')
            print(f'Runtime time-stepping: {runtime_ts} (This is currently not the correct value)')
            print(f'Speedup of schedule={schedule.NAME} for nProc={nProc}: {(runtime_ts / runtime):.2f} \n')
            print(f'Theoretical lower runtime bound: {optimal_runtime}')
            print(
                f'Theoretical maximum speedup compared to time stepping: {(runtime_ts / optimal_runtime):.2f} (This is currently not the correct value)')
            print('=============================')

        speedup = runtime_ts / runtime
        efficiency = speedup / nProc
        return speedup, efficiency, nProc

    def plotGraph(self, N, K, figSize=(6.4, 4.8), optimizeSerialParts=False):
        K = self.checkK(N=N, K=K)
        run = PintRun(blockIteration=self, nBlocks=N, kMax=K, optimizeSerialPool=optimizeSerialParts)
        run.plotGraph(figName=None if self.name is None else self.name + ' (graph)', figSize=figSize)

    def plotSchedule(self, N, K, nProc, schedule_type='BLOCK-BY-BLOCK', figSize=(8, 4.8), optimizeSerialParts=False):
        K = self.checkK(N=N, K=K)
        run = PintRun(blockIteration=self, nBlocks=N, kMax=K, optimizeSerialPool=optimizeSerialParts)
        schedule = getSchedule(taskPool=run.taskPool2, nProc=nProc, nPoints=N + 1, schedule_type=schedule_type)
        schedule.plot(figName=None if self.name is None else self.name + f' ({schedule.NAME} schedule)',
                      figSize=figSize)

    def checkK(self, N, K):
        if isinstance(K, int):
            return [0] + [K for _ in range(N)]
        elif isinstance(K, list) and len(K) == N:
            return [0] + K
        else:
            raise Exception('K must be a list of length N or an integer.')


# -----------------------------------------------------------------------------
# Inherited specialized class
# -----------------------------------------------------------------------------
ALGORITHMS: Dict[str, BlockIteration] = {}


def register(cls):
    ALGORITHMS[cls.__name__] = cls
    return cls


DEFAULT_PROP = {
    'implicit': 'phi**(-1)*chi',
    'explicit': 'F'}


@register
class Parareal(BlockIteration):
    needApprox = True

    def __init__(self, implicitForm=True, approxPred=True, **blockOps):
        if implicitForm:
            B00 = "(phi**(-1)*chi-phiApprox**(-1)*chi) * u_{n}^k"
            B01 = "phiApprox**(-1)*chi * u_{n}^{k+1}"
            predictor = "phiApprox**(-1)*chi" if approxPred else None
        else:
            B00 = "(F-G) * u_{n}^k"
            B01 = "G * u_{n}^{k+1}"
            predictor = "G" if approxPred else None
        update = f"{B00} + {B01}"
        propagator = DEFAULT_PROP['implicit'] if implicitForm \
            else DEFAULT_PROP['explicit']
        super().__init__(update, propagator, predictor,
                         rules=None, name='Parareal', **blockOps)


@register
class ABJ(BlockIteration):
    needApprox = True

    def __init__(self, implicitForm=True, approxPred=True, **blockOps):
        if implicitForm:
            B00 = "phiApprox**(-1)*chi * u_{n}^k"
            B10 = "(I-phiApprox**-1 * phi) * u_{n+1}^{k}"
            predictor = "phiApprox**(-1)*chi" if approxPred else None
        else:
            B00 = "G * u_{n}^k"
            B10 = "(I-G*F**(-1)) * u_{n}^{k+1}"
            predictor = "G" if approxPred else None
        update = f"{B10} + {B00}"
        blockOps['I'] = I
        propagator = DEFAULT_PROP['implicit'] if implicitForm \
            else DEFAULT_PROP['explicit']
        super().__init__(update, propagator, predictor,
                         rules=None, name='ABJ', **blockOps)


@register
class ABGS(BlockIteration):
    needApprox = True

    def __init__(self, implicitForm=True, approxPred=True, **blockOps):
        if implicitForm:
            B01 = "phiApprox**(-1)*chi * u_{n}^{k+1}"
            B10 = "(I-phiApprox**-1 * phi) * u_{n+1}^{k}"
            predictor = "phiApprox**(-1)*chi" if approxPred else None
        else:
            B01 = "G * u_{n}^{k+1}"
            B10 = "(I-G*F**(-1)) * u_{n}^{k+1}"
            predictor = "G" if approxPred else None
        update = f"{B10} + {B01}"
        blockOps['I'] = I
        propagator = DEFAULT_PROP['implicit'] if implicitForm \
            else DEFAULT_PROP['explicit']
        super().__init__(update, propagator, predictor,
                         rules=None, name='ABGS', **blockOps)


@register
class TMG(BlockIteration):
    needCoarse = True

    def __init__(self, coarsePred=True, **blockOps):
        omega = blockOps.get('omega', 1)
        blockOps.update({'omega': omega})
        phiC = "TCtoF * phiCoarse**(-1) * TFtoC"
        B01 = f"{phiC}*chi"" * u_{n}^{k+1}"
        B00 = f"omega*(phi**(-1)*chi - {phiC}*chi)"" * u_{n}^{k}"
        B10 = f"(1-omega)*(I-{phiC}*phi)"" * u_{n+1}^{k}"
        predictor = f"{phiC}*chi" if coarsePred else None
        update = f"{B10} + {B01} + {B00}"
        blockOps['I'] = I
        rule = [(f"TFtoC * TCtoF", 1)]
        propagator = DEFAULT_PROP['implicit']
        super().__init__(update, propagator, predictor,
                         rules=rule, name='TMG', **blockOps)
        self.omega = omega


@register
class PFASST(BlockIteration):
    needApprox = True
    needCoarse = True

    def __init__(self, coarsePred=True, **blockOps):
        phiC = "TCtoF * phiCoarseApprox**(-1) * TFtoC"
        B01 = f"{phiC}*chi"" * u_{n}^{k+1}"
        B00 = f"(phiApprox**(-1)*chi - {phiC}*phi*phiApprox**(-1)*chi)"" * u_{n}^{k}"
        B10 = f"(I-{phiC}*phi)*(I-phiApprox**(-1)*phi)"" * u_{n+1}^{k}"
        predictor = f"{phiC}*chi" if coarsePred else None
        update = f"{B10} + {B01} + {B00}"
        blockOps['I'] = I
        propagator = DEFAULT_PROP['implicit']
        super().__init__(update, propagator, predictor,
                         rules=None, name='PFASST', **blockOps)

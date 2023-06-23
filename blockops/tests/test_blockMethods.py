import numpy as np

from .data.methodData import results

from blockops.run import PintRun
from blockops.block import BlockOperator, I
from blockops.taskPool import TaskPool
from blockops.iteration import BlockIteration
from blockops import BlockProblem

nBlocks = 4

g = BlockOperator('G', cost=1)  # coarse solver
f = BlockOperator('F', cost=10)  # fine solver
r = BlockOperator('R', cost=0.2)  # restriction
p = BlockOperator('P', cost=0.2)  # prolongation (interpolation)

rules = [(r * p, I)]

phi = BlockOperator(r'\phi')  # integration operator
phiD = BlockOperator(r'\phi_{\Delta}')  # approximate integration operator
chi = BlockOperator(r'\chi')  # transmission operator

blockOps = dict(I=I, phi=phi, phiD=phiD, chi=chi)


def checkResults(method, run, pool):
    i = 0
    for key, value in run.facBlockRules.items():
        assert results[method]['blockRules'][i][0] == str(value["result"])
        assert results[method]['blockRules'][i][1] == str(value["rule"])
        i = i + 1

    i = 0
    for key, value in pool.pool.items():
        assert results[method]['taskPool'][i][0] == str(key)
        assert str(value.fullOP) in results[method]['taskPool'][i][1]
        i = i + 1


class TestMethods:

    def testPararealPhiChiNoPredictor(self):
        parareal = BlockIteration(
            update="(phi**(-1)-phiD**(-1))*chi*u_{n}^k + phiD**(-1)*chi* u_{n}^{k+1}",
            propagator=phi ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='PararealPhiChiNoPredictor', run=run, pool=pool)

    def testPararealPhiChi(self):
        parareal = BlockIteration(
            update="(phi**(-1)-phiD**(-1))*chi*u_{n}^k + phiD**(-1)*chi* u_{n}^{k+1}",
            propagator=phi ** (-1) * chi, predictor=phiD ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='PararealPhiChi', run=run, pool=pool)

    #
    def testPararealFGNoPredictor(self):
        parareal = BlockIteration(
            "(f - g) u_{n}^k + g * u_{n}^{k+1}",  # block iteration update formula
            propagator=f,
            rules=rules,  # list of rules (optional)
            f=f, g=g)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='PararealFGNoPredictor', run=run, pool=pool)

    #
    def testPararealFG(self):
        parareal = BlockIteration(
            "(f - g) u_{n}^k + g * u_{n}^{k+1}",  # block iteration update formula
            propagator=f, predictor=g,
            rules=rules,  # list of rules (optional)
            f=f, g=g)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='PararealFG', run=run, pool=pool)

    def testPararealSCFGNoPredictor(self):
        parareal = BlockIteration(
            "(f - p*g*r) u_{n}^k + p*g*r * u_{n}^{k+1}",  # block iteration update formula
            propagator=f,
            rules=rules,  # list of rules (optional)
            f=f, g=g, p=p, r=r)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='PararealSCFGNoPredictor', run=run, pool=pool)

    #
    def testPararealSCFG(self):
        parareal = BlockIteration(
            "(f - p*g*r) u_{n}^k + p*g*r * u_{n}^{k+1}",  # block iteration update formula
            propagator=f, predictor="p*g*r",
            rules=rules,  # list of rules (optional)
            f=f, g=g, p=p, r=r)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='PararealSCFG', run=run, pool=pool)

    def testBlockJacobiPredictorI(self):
        blockJacobi = BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=I,
            **blockOps)
        run = PintRun(blockIteration=blockJacobi, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='BlockJacobiPredictorI', run=run, pool=pool)

    def testBlockJacobiNoPredictor(self):
        blockJacobi = BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=blockJacobi, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='BlockJacobiNoPredictor', run=run, pool=pool)

    #
    def testBlockJacobi(self):
        blockJacobi = BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=phiD ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=blockJacobi, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='BlockJacobi', run=run, pool=pool)

    #
    def testApproxBlockGaussSeidelNoPredictor(self):
        approxBlockGaussSeidel = BlockIteration(
            update="phiD**(-1)*chi*u_{n}^{k+1} + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=approxBlockGaussSeidel, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='ApproxBlockGaussSeidelNoPredictor', run=run, pool=pool)

    #
    def testApproxBlockGaussSeidel(self):
        approxBlockGaussSeidel = BlockIteration(
            update="phiD**(-1)*chi*u_{n}^{k+1} + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=phiD ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=approxBlockGaussSeidel, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='ApproxBlockGaussSeidel', run=run, pool=pool)

    def testPFASST(self):
        prob = BlockProblem(1j, 2 * np.pi - 0.2, nBlocks, nPoints=5, scheme='Collocation')
        prob.setApprox('RungeKutta', rkScheme='BE')
        prob.setCoarseLevel(2)
        algo = prob.getBlockIteration('PFASST')
        run = PintRun(blockIteration=algo, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        pool = TaskPool(run=run)
        checkResults(method='PFASST', run=run, pool=pool)

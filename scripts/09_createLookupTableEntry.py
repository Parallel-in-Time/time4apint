import numpy as np

from blockops import BlockOperator, BlockIteration, I, PintRun
from blockops.lookup.lookupTable import picklePintRun
from blockops import BlockProblem

nBlocks = 100
kMax = 10

g = BlockOperator('G', cost=1)  # coarse solver
f = BlockOperator('F', cost=10)  # fine solver
r = BlockOperator('R', cost=0.2)  # restriction
p = BlockOperator('P', cost=0.2)  # prolongation (interpolation)

rules = [(r * p, I)]

phi = BlockOperator(r'\phi')  # integration operator
phiD = BlockOperator(r'\phi_{\Delta}')  # approximate integration operator
chi = BlockOperator(r'\chi')  # transmission operator

blockOps = dict(I=I, phi=phi, phiD=phiD, chi=chi)

PFASST = BlockProblem(1j, 2 * np.pi - 0.2, nBlocks, nPoints=5, scheme='Collocation')
PFASST.setApprox('RungeKutta', rkScheme='BE')
PFASST.setCoarseLevel(2)
PFASST = PFASST.getBlockIteration('PFASST')

algs = {
    'PararealPhiChi.pickle': BlockIteration(
        update="(phi**(-1)-phiD**(-1))*chi*u_{n}^k + phiD**(-1)*chi* u_{n}^{k+1}",
        propagator=phi ** (-1) * chi, predictor=phiD ** (-1) * chi,
        **blockOps),
    'PararealFGNoPredictor.pickle' : BlockIteration(
            "(f - g) u_{n}^k + g * u_{n}^{k+1}",  # block iteration update formula
            propagator=f,
            rules=rules,  # list of rules (optional)
            f=f, g=g),
    'PararealFG.pickle' : BlockIteration(
            "(f - g) u_{n}^k + g * u_{n}^{k+1}",  # block iteration update formula
            propagator=f, predictor=g,
            rules=rules,  # list of rules (optional)
            f=f, g=g),
    'PararealSCFGNoPredictor.pickle' : BlockIteration(
            "(f - p*g*r) u_{n}^k + p*g*r * u_{n}^{k+1}",  # block iteration update formula
            propagator=f,
            rules=rules,  # list of rules (optional)
            f=f, g=g, p=p, r=r),
    'testPararealSCFG.pickle' : BlockIteration(
            "(f - p*g*r) u_{n}^k + p*g*r * u_{n}^{k+1}",  # block iteration update formula
            propagator=f, predictor="p*g*r",
            rules=rules,  # list of rules (optional)
            f=f, g=g, p=p, r=r),
    'BlockJacobiPredictorI.pickle' : BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=I,
            **blockOps),
    'BlockJacobiNoPredictor.pickle' : BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi,
            **blockOps),
    'BlockJacobi.pickle' : BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=phiD ** (-1) * chi,
            **blockOps),
    'ApproxBlockGaussSeidelNoPredictor.pickle' : BlockIteration(
            update="phiD**(-1)*chi*u_{n}^{k+1} + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi,
            **blockOps),
    'ApproxBlockGaussSeidel.pickle' : BlockIteration(
            update="phiD**(-1)*chi*u_{n}^{k+1} + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=phiD ** (-1) * chi,
            **blockOps),
    'PFASST.pickle' : PFASST,
}

for key, value in algs.items():
    K = value.checkK(N=nBlocks, K=kMax)
    run = PintRun(blockIteration=value, nBlocks=nBlocks, kMax=K)
    picklePintRun(key, run, value)

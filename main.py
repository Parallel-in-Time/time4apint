# Import from the previous version
from Parareal import parareal, parareal_predictor, parareal_sc, parareal_predictor_sc
# Import from the new version
from block import BlockOperator, BlockIteration, one

# Common import
from PintRun import PintRun


# Previous version run
class Framework:
    def __init__(self):
        self.runs = []

    def testConfiguration(self, blockIteration, predictor, nBlocks, stop_crit):
        self.runs.append(PintRun(blockIteration=blockIteration, nBlocks=nBlocks, predictor=predictor))


a = Framework()

a.testConfiguration(
    blockIteration=parareal,
    predictor=parareal_predictor,
    nBlocks=4, stop_crit=10)
a.testConfiguration(
    blockIteration=parareal_sc,
    predictor=parareal_predictor_sc,
    nBlocks=4, stop_crit=10)

# a.testConfiguration(
#    blockIteration=sdc_block_jacobi,
#    predictor=sdc_block_jacobi_predictor,
#    nBlocks=4,
#    stop_crit=10
# )

# New version run
nBlocks = 4

g = BlockOperator('g')
f = BlockOperator('f')
r = BlockOperator('r')
p = BlockOperator('p')

rules = [(r*p, one)]
parareal_new = BlockIteration(
    "(f - g) u_{n}^k + g u_{n}^{k+1}",
    "g u_{n}^k",
    **locals())

PintRun(parareal_new, nBlocks, None)
pararealSC_new = BlockIteration(
    "(f - p*g*r) u_{n}^k + p*g*r * u_{n}^{k+1}",
    "p*g*r u_{n}^k",
    **locals())

PintRun(pararealSC_new, nBlocks, None)

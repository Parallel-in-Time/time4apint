# Import from the new version
from block import BlockOperator, BlockIteration, one

# Common import
from PintRun import PintRun

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

#TODO: The inverse is not implemented yet
#sdc_block_jacobi = BlockIteration(
#    "(i-d)^{-1}*h * u_{n}^k + (I-d)^{-1}*(q-qd)* u_{n+1}^{k}",
#    "i * u_{n}^k",
#    i=one, d = BlockOperator('d'), g = BlockOperator('q'), h = BlockOperator('h'))

#PintRun(pararealSC_new, nBlocks, rules)

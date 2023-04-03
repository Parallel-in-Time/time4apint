import numpy as np
from blockops import BlockProblem

tEnd = 2*np.pi-0.2
lam = 1j
nBlocks = 4

prob = BlockProblem(lam, tEnd, nBlocks, nPoints=5, scheme='Collocation')
prob.setApprox('RungeKutta', rkScheme='BE')
prob.setCoarseLevel(2)

algo = prob.getBlockIteration('PFASST')

algo.plotGraph(N=2,K=1)
algo.plotSchedule(
    N=4,
    K=4, #K=[1,2,3,4], 
    nProc=4)
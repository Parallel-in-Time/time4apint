from blockops import BlockOperator, BlockIteration, I

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)
N = 8
K = 3

predictor = "G"

parareal = BlockIteration(
    "(F - G) u_{n}^k + G * u_{n}^{k+1}",
    propagator="F", predictor="G", F=F, G=G, I=I, name='Parareal')

parareal.plotSchedule(N, K, nProc=N, schedulerType='LOWEST-COST-FIRST')
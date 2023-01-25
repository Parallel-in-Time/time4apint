import time

from blockops import BlockOperator, BlockIteration, I

nBlocks = 10

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)

predictor = "G"

parareal = BlockIteration(
    "(F - G) u_{n}^k + G u_{n}^{k+1}",
    propagator="F", predictor=predictor,
    F=F, G=G,
    name='Parareal')

ns = [1,5,10,12]
for item in ns:
    start = time.time()
    parareal.getRuntime(N=item, K=item, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'Runtime for N={item} and K={item}: {time.time()-start}')
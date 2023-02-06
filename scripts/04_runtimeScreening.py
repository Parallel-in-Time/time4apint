import time

from blockops import BlockOperator, BlockIteration, I

nBlocks = 10

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)
R = BlockOperator('R', cost=0.2)
P = BlockOperator('P', cost=0.2)

predictor = "G"

pararealSC = BlockIteration(
    "(F - P*G*R) u_{n}^k + P*G*R * u_{n}^{k+1}",
    propagator="F", predictor="P*G*R",
    rules=[(R * P, I)], F=F, G=G, R=R, P=P, I=I,
    name='PararealSC')

abj = BlockIteration(
    "G u_{n}^k + (I-G*F**(-1)) u_{n+1}^{k}",
    propagator="F", predictor=predictor,
    F=F, G=G, I=I,
    name='Approx. Block Jacobi')

abgs = BlockIteration(
    "G u_{n}^{k+1} + (I-G*F**(-1)) u_{n+1}^{k}",
    propagator="F", predictor=predictor,
    F=F, G=G, I=I,
    name='Approx. Block Gauss-Seidel')

ns = [14]
K=5
for item in ns:
    start = time.time()
    a = pararealSC.getRuntime(N=item, K=5, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'Parareal SC runtime for N={ns}, K={K}: {time.time()-start}')
    start = time.time()
    a = abj.getRuntime(N=item, K=K, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'ABJ runtime for N={ns}, K={K}: {time.time()-start}')
    start = time.time()
    a = abgs.getRuntime(N=item, K=3, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'abgs runtime for N={ns}, K={K}: {time.time()-start}')
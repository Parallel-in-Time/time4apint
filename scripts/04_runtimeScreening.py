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

ns = [12]
for item in ns:
    start = time.time()
    a, run = pararealSC.getRuntime(N=item, K=3, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'1:{time.time()-start}')
    start = time.time()
    a, run2 = pararealSC.getRuntime2(N=item, K=3, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'2:{time.time()-start}')
    print(f'Compare between 1 and 2: {run.taskPool == run2.taskPool}')
    run.plotGraph()
    run2.plotGraph()
    start = time.time()
    a, run = abj.getRuntime(N=item, K=3, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'1:{time.time()-start}')
    start = time.time()
    a, run2 = abj.getRuntime2(N=item, K=3, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'Compare between 1 and 2: {run.taskPool == run2.taskPool}')
    print(f'2:{time.time()-start}')
    start = time.time()
    run.plotGraph()
    run2.plotGraph()
    start = time.time()
    a, run = abgs.getRuntime(N=item, K=3, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'1:{time.time()-start}')
    start = time.time()
    a, run2 = abgs.getRuntime2(N=item, K=3, nProc=nBlocks, schedule_type='OPTIMAL')
    print(f'2:{time.time()-start}')
    print(f'Compare between 1 and 2: {run.taskPool == run2.taskPool}')
    run.plotGraph()
    run2.plotGraph()

a = 2
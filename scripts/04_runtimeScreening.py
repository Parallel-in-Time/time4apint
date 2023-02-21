import time

from blockops import BlockOperator, BlockIteration, I

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)
R = BlockOperator('R', cost=0.2)
P = BlockOperator('P', cost=0.2)

predictor = "G"

parareal = BlockIteration(
    "(F - G) u_{n}^k + G * u_{n}^{k+1}",
    propagator="F", predictor="G",
    rules=[(R * P, I)], F=F, G=G, I=I,
    name='Parareal')

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

for nBlocks in [50]:
    for k in [5]:
        for method in ['LCF', 'BLOCK-BY-BLOCK', 'OPTIMAL']:
            for blockIter in [parareal,pararealSC,abj, abgs]:
                print(f'N: {nBlocks}, K: {k}, method: {method}, blockIter {blockIter.name}')
                start = time.time()
                a = blockIter.getRuntime(N=nBlocks, K=k, nProc=nBlocks, schedule_type=method)
                print(f'{blockIter.name} runtime for N={nBlocks}, K={k}: {time.time()-start}, {a}')

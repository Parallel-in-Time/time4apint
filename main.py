from blockops import BlockOperator, BlockIteration, I

nBlocks = 4

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)
R = BlockOperator('R', cost=0.2)
P = BlockOperator('P', cost=0.2)

predictor = "G"
# predictor = None

import time

start = time.time()
parareal = BlockIteration(
    "(F - G) u_{n}^k + G u_{n}^{k+1}",
    propagator="F", predictor=predictor,
    F=F, G=G,
    name='Parareal')
pspeedup, efficiency, nProc = parareal.getPerformances(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks + 1,
                                                       schedule_type='LCF', verbose=True)
pspeedup, efficiency, nProc = parareal.getPerformances(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks,
                                                       schedule_type='BLOCK-BY-BLOCK', verbose=True)

parareal.plotGraph(N=nBlocks, K=[1, 2, 2, 2])
parareal.plotSchedule(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks + 1, schedule_type='LCF')
parareal.plotSchedule(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')

pararealSC = BlockIteration(
    "(F - P*G*R) u_{n}^k + P*G*R * u_{n}^{k+1}",
    propagator="F", predictor="P*G*R",
    rules=[(R * P, I)], F=F, G=G, R=R, P=P, I=I,
    name='PararealSC')
pspeedup, efficiency, nProc = pararealSC.getPerformances(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks + 1,
                                                         schedule_type='LCF', verbose=True)
pspeedup, efficiency, nProc = pararealSC.getPerformances(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks,
                                                         schedule_type='BLOCK-BY-BLOCK', verbose=True)
pararealSC.plotGraph(N=nBlocks, K=[1, 2, 2, 2])
pararealSC.plotSchedule(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks + 1, schedule_type='LCF')
pararealSC.plotSchedule(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')

abj = BlockIteration(
    "G u_{n}^k + (I-G*F**(-1)) u_{n+1}^{k}",
    propagator="F", predictor=predictor,
    F=F, G=G, I=I,
    name='Approx. Block Jacobi')
pspeedup, efficiency, nProc = abj.getPerformances(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks + 1, schedule_type='LCF',
                                                  verbose=True)
pspeedup, efficiency, nProc = abj.getPerformances(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks,
                                                  schedule_type='BLOCK-BY-BLOCK', verbose=True)
abj.plotGraph(N=nBlocks, K=[1, 2, 2, 2])
abj.plotSchedule(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks + 1, schedule_type='OPTIMAL')
abj.plotSchedule(N=nBlocks, K=[1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')

abgs = BlockIteration(
    "G u_{n}^{k+1} + (I-G*F**(-1)) u_{n+1}^{k}",
    propagator="F", predictor=predictor,
    F=F, G=G, I=I,
    name='Approx. Block Gauss-Seidel')
pspeedup, efficiency, nProc = abgs.getPerformances(N=nBlocks, K=2, nProc=nBlocks + 1, schedule_type='LCF', verbose=True)
pspeedup, efficiency, nProc = abgs.getPerformances(N=nBlocks, K=2, nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK',
                                                   verbose=True)
abgs.plotGraph(N=nBlocks, K=2)
abgs.plotSchedule(N=nBlocks, K=2, nProc=nBlocks + 1, schedule_type='OPTIMAL')
abgs.plotSchedule(N=nBlocks, K=2, nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')

from blockops import BlockOperator, BlockIteration, I

nBlocks = 4

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)
R = BlockOperator('R', cost=0.2)
P = BlockOperator('P', cost=0.2)

predictor = "G"
# predictor = None

parareal = BlockIteration(
    "(F - G) u_{n}^k + G u_{n}^{k+1}",
    propagator="F", predictor=predictor,
    F=F, G=G,
    name='Parareal')
parareal.speedup(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='OPTIMAL')
parareal.speedup(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')
#parareal.plotGraph(N=nBlocks, K=[0, 1, 2, 2, 2])
parareal.plotSchedule(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='OPTIMAL')
parareal.plotSchedule(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')

pararealSC = BlockIteration(
    "(F - P*G*R) u_{n}^k + P*G*R * u_{n}^{k+1}",
    propagator="F", predictor="P*G*R",
    rules=[(R * P, I)], F=F, G=G, R=R, P=P, I=I,
    name='PararealSC')
pararealSC.speedup(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='OPTIMAL')
pararealSC.speedup(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')
pararealSC.plotGraph(N=nBlocks, K=[0, 1, 2, 2, 2])
pararealSC.plotSchedule(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='OPTIMAL')
pararealSC.plotSchedule(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')

abj = BlockIteration(
    "G u_{n}^k + (I-G*F**(-1)) u_{n+1}^{k}",
    propagator="F", predictor=predictor,
    F=F, G=G, I=I,
    name='Approx. Block Jacobi')
abj.speedup(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='OPTIMAL')
abj.speedup(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')
abj.plotGraph(N=nBlocks, K=[0, 1, 2, 2, 2])
abj.plotSchedule(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='OPTIMAL')
abj.plotSchedule(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')


abgs = BlockIteration(
    "G u_{n}^{k+1} + (I-G*F**(-1)) u_{n+1}^{k}",
    propagator="F", predictor=predictor,
    F=F, G=G, I=I,
    name='Approx. Block Gauss-Seidel')
abgs.speedup(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='OPTIMAL')
abgs.speedup(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')
abgs.plotGraph(N=nBlocks, K=[0, 1, 2, 2, 2])
abgs.plotSchedule(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='OPTIMAL')
abgs.plotSchedule(N=nBlocks, K=[0, 1, 2, 2, 2], nProc=nBlocks, schedule_type='BLOCK-BY-BLOCK')


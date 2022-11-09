from blockops import BlockOperator, BlockIteration, one

nBlocks = 4

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)
R = BlockOperator('R', cost=0.2)
P = BlockOperator('P', cost=0.2)

predictor = "G u_{n}^k"

parareal = BlockIteration(
    "(F - G) u_{n}^k + G u_{n}^{k+1}",
    #predictor,
    F=F, G=G)
parareal.speedup(N=nBlocks, K=[0, 1, 2, 2, 2])
parareal.plotGraph(N=nBlocks, K=[0, 1, 2, 2, 2])

pararealSC = BlockIteration(
    "(F - P*G*R) u_{n}^k + P*G*R * u_{n}^{k+1}",
    "P*G*R u_{n}^k",
    rules=[(R * P, one)], F=F, G=G, R=R, P=P, I=one)
pararealSC.speedup(N=nBlocks, K=[0, 1, 2, 2, 2])
pararealSC.plotGraph(N=nBlocks, K=[0, 1, 2, 2, 2])

abj = BlockIteration(
    "G u_{n}^k + (I-G*F**(-1)) u_{n+1}^{k}",
    predictor,
    F=F, G=G, I=one)
abj.speedup(N=nBlocks, K=[0, 1, 2, 2, 2])
abj.plotGraph(N=nBlocks, K=[0, 1, 2, 2, 2])

abgs = BlockIteration(
    "G u_{n}^{k+1} + (I-G*F**(-1)) u_{n+1}^{k}",
    predictor,
    F=F, G=G, I=one)
abgs.speedup(N=nBlocks, K=[0, 1, 2, 2, 2])
abgs.plotGraph(N=nBlocks, K=[0, 1, 2, 2, 2])

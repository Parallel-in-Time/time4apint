from blockops import BlockOperator, BlockIteration, one, PintRun

nBlocks = 4

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)
R = BlockOperator('R', cost=0)
P = BlockOperator('P', cost=0)

predictor = "G u_{n}^k"

parareal = BlockIteration(
    "(F - G) u_{n}^k + G u_{n}^{k+1}",
    predictor,
    F=F, G=G)
PintRun(parareal, nBlocks)

pararealSC = BlockIteration(
    "(F - P*G*R) u_{n}^k + P*G*R * u_{n}^{k+1}",
    "P*G*R u_{n}^k",
    rules=[(R*P, one)], F=F, G=G, R=R, P=P, I=one)
PintRun(pararealSC, nBlocks)

abj = BlockIteration(
    "G u_{n}^k + (I-G*F**(-1)) u_{n+1}^{k}",
    predictor,
    F=F, G=G, I=one)
PintRun(abj, nBlocks)

abgs = BlockIteration(
    "G u_{n}^{k+1} + (I-G*F**(-1)) u_{n+1}^{k}",
    predictor,
    F=F, G=G, I=one)
PintRun(abgs, nBlocks)

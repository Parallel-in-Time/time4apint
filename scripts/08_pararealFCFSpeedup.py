from blockops import BlockOperator, BlockIteration

G = BlockOperator('G', cost=0.1)
F = BlockOperator('F', cost=1)
N = 8
K = 3

blockOps = dict(F=F, G=G)

parareal_fcf = BlockIteration(
    update="(F-G)*F*u_{n-1}^k + G*u_{n}^{k+1}",
    predictor="G", propagator="F", **blockOps)
fig = parareal_fcf.plotSchedule(
    N=N, K=K, nProc=N, schedulerType="BLOCK-BY-BLOCK")
fig.show()

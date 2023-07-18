from blockops import BlockOperator, BlockIteration

G = BlockOperator('G', cost=1)
F = BlockOperator('F', cost=10)
N = 8
K = 3
schedulerType = 'BLOCK-BY-BLOCK'

predictor = "G"

parareal = BlockIteration(
    "(F - G) u_{n}^k + G * u_{n}^{k+1}",
    propagator="F", predictor="G", F=F, G=G, name='Parareal')

fig = parareal.plotSchedule(N, K, nProc=N, schedulerType=schedulerType)
fig.show()

time = parareal.getRuntime(N, K, N, schedulerType=schedulerType)
print(f"Runtime = {time}")
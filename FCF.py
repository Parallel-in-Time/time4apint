from blockops import BlockOperator, BlockIteration, I

nBlocks = 8

phi = BlockOperator(r'\phi', cost=4)  # integration operator
phiD = BlockOperator(r'\phi_{\Delta}', cost=1)  # inverse approximate integration operator
chi = BlockOperator(r'\chi', cost=0.1)  # transmission operator

blockOps = dict(I=I, phi=phi, phiD=phiD, chi=chi)

parareal_fcf = BlockIteration(
    update="(I-phiD**(-1))*phi**(-1)*chi*phi**(-1)*chi*u_{n-1}^k + phiD**(-1)*chi* u_{n}^{k+1}",
    predictor="phiD**(-1)*chi",
    propagator=phi**(-1)*chi,
    **blockOps)
parareal_fcf.plotGraph(N=nBlocks, K=nBlocks,  figSize=(6.4*2, 4.8*2))
# parareal_fcf.plotGraphForOneBlock(N=nBlocks, K=nBlocks, plotBlock=4, plotIter=2,  figSize=(6.4*2, 4.8*2))
parareal_fcf.plotSchedule(N=nBlocks, K=nBlocks, nProc=nBlocks, schedulerType="BLOCK-BY-BLOCK")


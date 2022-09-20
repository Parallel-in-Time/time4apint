from BlockOperator import BlockOperator
from BlockComponent import BlockComponent
from BlockIteration import BlockIteration
from Predictor import Predictor
from Rule import Rule

# SDC

imq = BlockComponent(name='imq', cost=1, matrix=1)
imqdInv = BlockComponent(name='imqdInv', cost=1,matrix=1)
H = BlockComponent(name='H', cost=1, matrix=1)
i = BlockComponent(name='i', cost=1,matrix=1)

op1 = BlockOperator(blockComponent=i, depTime=0, depIter=-1, sign='+')
op2 = BlockOperator(blockComponent=imqdInv*imq, depTime=0, depIter=-1, sign='-')
op3 = BlockOperator(blockComponent=imqdInv*H, depTime=-1, depIter=-1, sign='+')


sdc_block_jacobi_predictor = Predictor(predictionOperators=[op3])
sdc_block_jacobi = BlockIteration(blockOperators=[op1, op2, op3])

#g = BlockComponent(name='g', cost=1, matrix=1)
#f = BlockComponent(name='f', cost=4, matrix=1)
#
#op1 = BlockOperator(blockComponent=f, depTime=-1, depIter=-1, sign='+')
#op2 = BlockOperator(blockComponent=g, depTime=-1, depIter=-1, sign='-')
#op3 = BlockOperator(blockComponent=g, depTime=-1, depIter=0, sign='+')
#
#parareal = BlockIteration(blockOperators=[op1, op2, op3])
#parareal_predictor = Predictor(predictionOperators=[op3])
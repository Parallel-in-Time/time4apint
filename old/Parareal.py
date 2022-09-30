from BlockOperator import BlockOperator
from BlockComponent import BlockComponent
from BlockIteration import BlockIteration
from Predictor import Predictor
from Rule import Rule

# Parareal

g = BlockComponent(name='g', cost=1, matrix=1)
f = BlockComponent(name='f', cost=4, matrix=1)

op1 = BlockOperator(blockComponent=f, depTime=-1, depIter=-1, sign='+')
op2 = BlockOperator(blockComponent=g, depTime=-1, depIter=-1, sign='-')
op3 = BlockOperator(blockComponent=g, depTime=-1, depIter=0, sign='+')

parareal = BlockIteration(blockOperators=[op1, op2, op3])
parareal_predictor = Predictor(predictionOperators=[op3])

# Parareal with spatial coarsening

r = BlockComponent(name='r', cost=0, matrix=1)
p = BlockComponent(name='p', cost=0, matrix=1)

op1 = BlockOperator(blockComponent=f, depTime=-1, depIter=-1, sign='+')
op2 = BlockOperator(blockComponent=p * g * r, depTime=-1, depIter=-1, sign='-')
op3 = BlockOperator(blockComponent=p * g * r, depTime=-1, depIter=0, sign='+')

rule1 = Rule(blockOperator1=r, op='*', blockOperator2=p, result=1)

parareal_sc = BlockIteration(blockOperators=[op1, op2, op3], rules=[rule1])
parareal_predictor_sc = Predictor(predictionOperators=[op3], rules=[rule1])

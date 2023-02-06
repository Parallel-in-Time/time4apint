import numpy as np
import pytest
import sympy as sy

from ..run import PintRun, NameGenerator
from ..block import BlockOperator
from ..iteration import BlockIteration


class TestRun:
    G = BlockOperator('G', cost=1)
    F = BlockOperator('F', cost=10)
    R = BlockOperator('R', cost=0.2)
    P = BlockOperator('P', cost=0.2)

    predictor = "G"

    parareal = BlockIteration(
        "(F - G) u_{n}^k + G u_{n}^{k+1}",
        propagator="F", predictor=predictor,
        F=F, G=G,
        name='Parareal')

    run = PintRun(parareal, 3, [0, 3, 3, 3])

    def testCreateSymbolForUnk(self):
        # n<0
        res = self.run.createSymbolForUnk(n=-1, k=0)
        assert sy.symbols(f'u_{0}^{0}', commutative=False) == res

        # k<kMax
        res = self.run.createSymbolForUnk(n=2, k=2)
        assert sy.symbols(f'u_{2}^{2}', commutative=False) == res

        # k>kMax
        res = self.run.createSymbolForUnk(n=2, k=5)
        assert sy.symbols(f'u_{2}^{3}', commutative=False) == res

    def testExtractTasksFromRule(self):
        res = sy.symbols(f'r', commutative=False)
        res1 = sy.symbols(f'r_1', commutative=False)
        res2 = sy.symbols(f'r_2', commutative=False)
        res3 = sy.symbols(f'r_3', commutative=False)
        u12 = sy.symbols(f'u_1^2', commutative=False)
        u11 = sy.symbols(f'u_1^1', commutative=False)
        u22 = sy.symbols(f'u_2^2', commutative=False)
        op = self.F.symbol * u12 + self.G.symbol * u22 - self.G.symbol * u11
        pool = self.run.extractTasksFromRule(op=op, res=res)

        res = {
            res1: {'op': 'o', 'task': [self.F.symbol, u12]},
            res2: {'op': 'o', 'task': [self.G.symbol, u22]},
            res3: {'op': 'o', 'task': [self.G.symbol, u11]},
            res: {'op': '+', 'task': [res1, res2, res3]},
        }
        assert res == pool

        res = sy.symbols(f'q', commutative=False)
        op = self.F.symbol * u12
        pool = self.run.extractTasksFromRule(op=op, res=res)
        res = {
            res: {'op': 'o', 'task': [self.F.symbol, u12]}
        }
        assert res == pool

    def testTaskGenerator(self):
        #TODO
        pass

    def testCreateIterationRule(self):
        pass



class TestNameGenerator:

    def testConstructor(self):
        tmp = NameGenerator('test')
        assert 'test' == tmp.prefix
        assert tmp.counter == 0

    def testGet(self):
        tmp = NameGenerator('test')
        assert sy.symbols(f'test', commutative=False) == tmp.get()

        assert sy.symbols(f'test_1', commutative=False) == tmp.get()
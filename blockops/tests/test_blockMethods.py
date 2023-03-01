import numpy as np
import pytest

from ..run import PintRun
from ..block import BlockOperator,I
from ..iteration import BlockIteration

nBlocks = 4

g = BlockOperator('G', cost=1)  # coarse solver
f = BlockOperator('F', cost=10)  # fine solver
r = BlockOperator('R', cost=0.2)  # restriction
p = BlockOperator('P', cost=0.2)  # prolongation (interpolation)

rules = [(r*p, I)]

phi = BlockOperator(r'\phi')  # integration operator
phiD = BlockOperator(r'\phi_{\Delta}')  # approximate integration operator
chi = BlockOperator(r'\chi')  # transmission operator

blockOps = dict(I=I, phi=phi, phiD=phiD, chi=chi)

class TestMethods:

    def testPararealPhiChiNoPredictor(self):
        parareal = BlockIteration(
            update="(phi**(-1)-phiD**(-1))*chi*u_{n}^k + phiD**(-1)*chi* u_{n}^{k+1}",
            propagator=phi ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0,4,4,4,4])

        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0", r"0"],
            [r"u_2^0", r"0"],
            [r"u_3^0", r"0"],
            [r"u_4^0", r"0"],
            [r"u_1^1_5", r"\chi*u_0^0"],
            [r"u_1^1_6", r"\phi**(-1)*\chi*u_0^0"],
            [r"u_1^1", r"\phi**(-1)*\chi*u_0^0"],
            [r"u_2^1_7", r"\chi*u_1^0"],
            [r"u_2^1_8", r"\phi**(-1)*\chi*u_1^0"],
            [r"u_2^1_10", r"-\chi*(u_1^0 - u_1^1)"],
            [r"u_2^1_11", r"-\phi_{\Delta}**(-1)*\chi*(u_1^0 - u_1^1)"],
            [r"u_2^1", r"\phi**(-1)*\chi*u_1^0 - \phi_{\Delta}**(-1)*\chi*(u_1^0 - u_1^1)"],
            [r"u_3^1_12", r"\chi*u_2^0"],
            [r"u_3^1_13", r"\phi**(-1)*\chi*u_2^0"],
            [r"u_3^1_15", r"-\chi*(u_2^0 - u_2^1)"],
            [r"u_3^1_16", r"-\phi_{\Delta}**(-1)*\chi*(u_2^0 - u_2^1)"],
            [r"u_3^1", r"\phi**(-1)*\chi*u_2^0 - \phi_{\Delta}**(-1)*\chi*(u_2^0 - u_2^1)"],
            [r"u_4^1_17", r"\chi*u_3^0"],
            [r"u_4^1_18", r"\phi**(-1)*\chi*u_3^0"],
            [r"u_4^1_20", r"-\chi*(u_3^0 - u_3^1)"],
            [r"u_4^1_21", r"-\phi_{\Delta}**(-1)*\chi*(u_3^0 - u_3^1)"],
            [r"u_4^1", r"\phi**(-1)*\chi*u_3^0 - \phi_{\Delta}**(-1)*\chi*(u_3^0 - u_3^1)"],
            [r"u_2^2_22", r"\chi*u_1^1"],
            [r"u_2^2_23", r"\phi**(-1)*\chi*u_1^1"],
            [r"u_2^2", r"\phi**(-1)*\chi*u_1^1"],
            [r"u_3^2_24", r"\chi*u_2^1"],
            [r"u_3^2_25", r"\phi**(-1)*\chi*u_2^1"],
            [r"u_3^2_27", r"-\chi*(u_2^1 - u_2^2)"],
            [r"u_3^2_28", r"-\phi_{\Delta}**(-1)*\chi*(u_2^1 - u_2^2)"],
            [r"u_3^2", r"\phi**(-1)*\chi*u_2^1 - \phi_{\Delta}**(-1)*\chi*(u_2^1 - u_2^2)"],
            [r"u_4^2_29", r"\chi*u_3^1"],
            [r"u_4^2_30", r"\phi**(-1)*\chi*u_3^1"],
            [r"u_4^2_32", r"-\chi*(u_3^1 - u_3^2)"],
            [r"u_4^2_33", r"-\phi_{\Delta}**(-1)*\chi*(u_3^1 - u_3^2)"],
            [r"u_4^2", r"\phi**(-1)*\chi*u_3^1 - \phi_{\Delta}**(-1)*\chi*(u_3^1 - u_3^2)"],
            [r"u_3^3_34", r"\chi*u_2^2"],
            [r"u_3^3_35", r"\phi**(-1)*\chi*u_2^2"],
            [r"u_3^3", r"\phi**(-1)*\chi*u_2^2"],
            [r"u_4^3_36", r"\chi*u_3^2"],
            [r"u_4^3_37", r"\phi**(-1)*\chi*u_3^2"],
            [r"u_4^3_39", r"-\chi*(u_3^2 - u_3^3)"],
            [r"u_4^3_40", r"-\phi_{\Delta}**(-1)*\chi*(u_3^2 - u_3^3)"],
            [r"u_4^3", r"\phi**(-1)*\chi*u_3^2 - \phi_{\Delta}**(-1)*\chi*(u_3^2 - u_3^3)"],
            [r"u_4^4_41", r"\chi*u_3^3"],
            [r"u_4^4_42", r"\phi**(-1)*\chi*u_3^3"],
            [r"u_4^4", r"\phi**(-1)*\chi*u_3^3"]
        ]
        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testPararealPhiChi(self):
        parareal = BlockIteration(
            update="(phi**(-1)-phiD**(-1))*chi*u_{n}^k + phiD**(-1)*chi* u_{n}^{k+1}",
            propagator=phi ** (-1) * chi, predictor=phiD**(-1)*chi,
            **blockOps)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0,4,4,4,4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0_1", r"\chi*u_0^0"],
            [r"u_1^0_2", r"\phi_{\Delta}**(-1)*\chi*u_0^0"],
            [r"u_1^0", r"\phi_{\Delta}**(-1)*\chi*u_0^0"],
            [r"u_2^0_3", r"\chi*u_1^0"],
            [r"u_2^0_4", r"\phi_{\Delta}**(-1)*\chi*u_1^0"],
            [r"u_2^0", r"\phi_{\Delta}**(-1)*\chi*u_1^0"],
            [r"u_3^0_5", r"\chi*u_2^0"],
            [r"u_3^0_6", r"\phi_{\Delta}**(-1)*\chi*u_2^0"],
            [r"u_3^0", r"\phi_{\Delta}**(-1)*\chi*u_2^0"],
            [r"u_4^0_7", r"\chi*u_3^0"],
            [r"u_4^0_8", r"\phi_{\Delta}**(-1)*\chi*u_3^0"],
            [r"u_4^0", r"\phi_{\Delta}**(-1)*\chi*u_3^0"],
            [r"u_1^1_9", r"\phi**(-1)*\chi*u_0^0"],
            [r"u_1^1", r"\phi**(-1)*\chi*u_0^0"],
            [r"u_2^1_11", r"\phi**(-1)*\chi*u_1^0"],
            [r"u_2^1_12", r"\chi*u_1^1"],
            [r"u_2^1_13", r"\phi_{\Delta}**(-1)*\chi*u_1^1"],
            [r"u_2^1", r"\phi**(-1)*\chi*u_1^0 + \phi_{\Delta}**(-1)*\chi*u_1^1 - u_2^0"],
            [r"u_3^1_15", r"\phi**(-1)*\chi*u_2^0"],
            [r"u_3^1_16", r"\chi*u_2^1"],
            [r"u_3^1_17", r"\phi_{\Delta}**(-1)*\chi*u_2^1"],
            [r"u_3^1", r"\phi**(-1)*\chi*u_2^0 + \phi_{\Delta}**(-1)*\chi*u_2^1 - u_3^0"],
            [r"u_4^1_19", r"\phi**(-1)*\chi*u_3^0"],
            [r"u_4^1_20", r"\chi*u_3^1"],
            [r"u_4^1_21", r"\phi_{\Delta}**(-1)*\chi*u_3^1"],
            [r"u_4^1", r"\phi**(-1)*\chi*u_3^0 + \phi_{\Delta}**(-1)*\chi*u_3^1 - u_4^0"],
            [r"u_2^2_22", r"\phi**(-1)*\chi*u_1^1"],
            [r"u_2^2", r"\phi**(-1)*\chi*u_1^1"],
            [r"u_3^2_23", r"\phi**(-1)*\chi*u_2^1"],
            [r"u_3^2_25", r"-\chi*(u_2^1 - u_2^2)"],
            [r"u_3^2_26", r"-\phi_{\Delta}**(-1)*\chi*(u_2^1 - u_2^2)"],
            [r"u_3^2", r"\phi**(-1)*\chi*u_2^1 - \phi_{\Delta}**(-1)*\chi*(u_2^1 - u_2^2)"],
            [r"u_4^2_27", r"\phi**(-1)*\chi*u_3^1"],
            [r"u_4^2_29", r"-\chi*(u_3^1 - u_3^2)"],
            [r"u_4^2_30", r"-\phi_{\Delta}**(-1)*\chi*(u_3^1 - u_3^2)"],
            [r"u_4^2", r"\phi**(-1)*\chi*u_3^1 - \phi_{\Delta}**(-1)*\chi*(u_3^1 - u_3^2)"],
            [r"u_3^3_31", r"\chi*u_2^2"],
            [r"u_3^3_32", r"\phi**(-1)*\chi*u_2^2"],
            [r"u_3^3", r"\phi**(-1)*\chi*u_2^2"],
            [r"u_4^3_33", r"\chi*u_3^2"],
            [r"u_4^3_34", r"\phi**(-1)*\chi*u_3^2"],
            [r"u_4^3_36", r"-\chi*(u_3^2 - u_3^3)"],
            [r"u_4^3_37", r"-\phi_{\Delta}**(-1)*\chi*(u_3^2 - u_3^3)"],
            [r"u_4^3", r"\phi**(-1)*\chi*u_3^2 - \phi_{\Delta}**(-1)*\chi*(u_3^2 - u_3^3)"],
            [r"u_4^4_38", r"\chi*u_3^3"],
            [r"u_4^4_39", r"\phi**(-1)*\chi*u_3^3"],
            [r"u_4^4", r"\phi**(-1)*\chi*u_3^3"]
        ]
        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1


    def testPararealFGNoPredictor(self):
        parareal = BlockIteration(
            "(f - g) u_{n}^k + g * u_{n}^{k+1}",  # block iteration update formula
            propagator=f,
            rules=rules,  # list of rules (optional)
            f=f, g=g)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0", r"0"],
            [r"u_2^0", r"0"],
            [r"u_3^0", r"0"],
            [r"u_4^0", r"0"],
            [r"u_1^1_5", r"F*u_0^0"],
            [r"u_1^1", r"F*u_0^0"],
            [r"u_2^1_6", r"F*u_1^0"],
            [r"u_2^1_8", r"-G*(u_1^0 - u_1^1)"],
            [r"u_2^1", r"F*u_1^0 - G*(u_1^0 - u_1^1)"],
            [r"u_3^1_9", r"F*u_2^0"],
            [r"u_3^1_11", r"-G*(u_2^0 - u_2^1)"],
            [r"u_3^1", r"F*u_2^0 - G*(u_2^0 - u_2^1)"],
            [r"u_4^1_12", r"F*u_3^0"],
            [r"u_4^1_14", r"-G*(u_3^0 - u_3^1)"],
            [r"u_4^1", r"F*u_3^0 - G*(u_3^0 - u_3^1)"],
            [r"u_2^2_15", r"F*u_1^1"],
            [r"u_2^2", r"F*u_1^1"],
            [r"u_3^2_16", r"F*u_2^1"],
            [r"u_3^2_18", r"-G*(u_2^1 - u_2^2)"],
            [r"u_3^2", r"F*u_2^1 - G*(u_2^1 - u_2^2)"],
            [r"u_4^2_19", r"F*u_3^1"],
            [r"u_4^2_21", r"-G*(u_3^1 - u_3^2)"],
            [r"u_4^2", r"F*u_3^1 - G*(u_3^1 - u_3^2)"],
            [r"u_3^3_22", r"F*u_2^2"],
            [r"u_3^3", r"F*u_2^2"],
            [r"u_4^3_23", r"F*u_3^2"],
            [r"u_4^3_25", r"-G*(u_3^2 - u_3^3)"],
            [r"u_4^3", r"F*u_3^2 - G*(u_3^2 - u_3^3)"],
            [r"u_4^4_26", r"F*u_3^3"],
            [r"u_4^4", r"F*u_3^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testPararealFG(self):
        parareal = BlockIteration(
            "(f - g) u_{n}^k + g * u_{n}^{k+1}",  # block iteration update formula
            propagator=f, predictor=g,
            rules=rules,  # list of rules (optional)
            f=f, g=g)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0_1", r"G*u_0^0"],
            [r"u_1^0", r"G*u_0^0"],
            [r"u_2^0_2", r"G*u_1^0"],
            [r"u_2^0", r"G*u_1^0"],
            [r"u_3^0_3", r"G*u_2^0"],
            [r"u_3^0", r"G*u_2^0"],
            [r"u_4^0_4", r"G*u_3^0"],
            [r"u_4^0", r"G*u_3^0"],
            [r"u_1^1_5", r"F*u_0^0"],
            [r"u_1^1", r"F*u_0^0"],
            [r"u_2^1_7", r"F*u_1^0"],
            [r"u_2^1_8", r"G*u_1^1"],
            [r"u_2^1", r"F*u_1^0 + G*u_1^1 - u_2^0"],
            [r"u_3^1_10", r"F*u_2^0"],
            [r"u_3^1_11", r"G*u_2^1"],
            [r"u_3^1", r"F*u_2^0 + G*u_2^1 - u_3^0"],
            [r"u_4^1_13", r"F*u_3^0"],
            [r"u_4^1_14", r"G*u_3^1"],
            [r"u_4^1", r"F*u_3^0 + G*u_3^1 - u_4^0"],
            [r"u_2^2_15", r"F*u_1^1"],
            [r"u_2^2", r"F*u_1^1"],
            [r"u_3^2_16", r"F*u_2^1"],
            [r"u_3^2_18", r"-G*(u_2^1 - u_2^2)"],
            [r"u_3^2", r"F*u_2^1 - G*(u_2^1 - u_2^2)"],
            [r"u_4^2_19", r"F*u_3^1"],
            [r"u_4^2_21", r"-G*(u_3^1 - u_3^2)"],
            [r"u_4^2", r"F*u_3^1 - G*(u_3^1 - u_3^2)"],
            [r"u_3^3_22", r"F*u_2^2"],
            [r"u_3^3", r"F*u_2^2"],
            [r"u_4^3_23", r"F*u_3^2"],
            [r"u_4^3_25", r"-G*(u_3^2 - u_3^3)"],
            [r"u_4^3", r"F*u_3^2 - G*(u_3^2 - u_3^3)"],
            [r"u_4^4_26", r"F*u_3^3"],
            [r"u_4^4", r"F*u_3^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testPararealSCFGNoPredictor(self):
        parareal = BlockIteration(
            "(f - p*g*r) u_{n}^k + p*g*r * u_{n}^{k+1}",  # block iteration update formula
            propagator=f,
            rules=rules,  # list of rules (optional)
            f=f, g=g, p=p, r=r)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0", r"0"],
            [r"u_2^0", r"0"],
            [r"u_3^0", r"0"],
            [r"u_4^0", r"0"],
            [r"u_1^1_5", r"F*u_0^0"],
            [r"u_1^1", r"F*u_0^0"],
            [r"u_2^1_6", r"F*u_1^0"],
            [r"u_2^1_8", r"-R*(u_1^0 - u_1^1)"],
            [r"u_2^1_9", r"-G*R*(u_1^0 - u_1^1)"],
            [r"u_2^1_10", r"-P*G*R*(u_1^0 - u_1^1)"],
            [r"u_2^1", r"F*u_1^0 - P*G*R*(u_1^0 - u_1^1)"],
            [r"u_3^1_11", r"F*u_2^0"],
            [r"u_3^1_13", r"-R*(u_2^0 - u_2^1)"],
            [r"u_3^1_14", r"-G*R*(u_2^0 - u_2^1)"],
            [r"u_3^1_15", r"-P*G*R*(u_2^0 - u_2^1)"],
            [r"u_3^1", r"F*u_2^0 - P*G*R*(u_2^0 - u_2^1)"],
            [r"u_4^1_16", r"F*u_3^0"],
            [r"u_4^1_18", r"-R*(u_3^0 - u_3^1)"],
            [r"u_4^1_19", r"-G*R*(u_3^0 - u_3^1)"],
            [r"u_4^1_20", r"-P*G*R*(u_3^0 - u_3^1)"],
            [r"u_4^1", r"F*u_3^0 - P*G*R*(u_3^0 - u_3^1)"],
            [r"u_2^2_21", r"F*u_1^1"],
            [r"u_2^2", r"F*u_1^1"],
            [r"u_3^2_22", r"F*u_2^1"],
            [r"u_3^2_24", r"-R*(u_2^1 - u_2^2)"],
            [r"u_3^2_25", r"-G*R*(u_2^1 - u_2^2)"],
            [r"u_3^2_26", r"-P*G*R*(u_2^1 - u_2^2)"],
            [r"u_3^2", r"F*u_2^1 - P*G*R*(u_2^1 - u_2^2)"],
            [r"u_4^2_27", r"F*u_3^1"],
            [r"u_4^2_29", r"-R*(u_3^1 - u_3^2)"],
            [r"u_4^2_30", r"-G*R*(u_3^1 - u_3^2)"],
            [r"u_4^2_31", r"-P*G*R*(u_3^1 - u_3^2)"],
            [r"u_4^2", r"F*u_3^1 - P*G*R*(u_3^1 - u_3^2)"],
            [r"u_3^3_32", r"F*u_2^2"],
            [r"u_3^3", r"F*u_2^2"],
            [r"u_4^3_33", r"F*u_3^2"],
            [r"u_4^3_35", r"-R*(u_3^2 - u_3^3)"],
            [r"u_4^3_36", r"-G*R*(u_3^2 - u_3^3)"],
            [r"u_4^3_37", r"-P*G*R*(u_3^2 - u_3^3)"],
            [r"u_4^3", r"F*u_3^2 - P*G*R*(u_3^2 - u_3^3)"],
            [r"u_4^4_38", r"F*u_3^3"],
            [r"u_4^4", r"F*u_3^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testPararealSCFG(self):
        parareal = BlockIteration(
            "(f - p*g*r) u_{n}^k + p*g*r * u_{n}^{k+1}",  # block iteration update formula
            propagator=f, predictor="p*g*r",
            rules=rules,  # list of rules (optional)
            f=f, g=g, p=p, r=r)
        run = PintRun(blockIteration=parareal, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0_1", r"R*u_0^0"],
            [r"u_1^0_2", r"G*R*u_0^0"],
            [r"u_1^0_3", r"P*G*R*u_0^0"],
            [r"u_1^0", r"P*G*R*u_0^0"],
            [r"u_2^0_4", r"G**2*R*u_0^0"],
            [r"u_2^0_5", r"P*G**2*R*u_0^0"],
            [r"u_2^0", r"P*G**2*R*u_0^0"],
            [r"u_3^0_6", r"G**3*R*u_0^0"],
            [r"u_3^0_7", r"P*G**3*R*u_0^0"],
            [r"u_3^0", r"P*G**3*R*u_0^0"],
            [r"u_4^0_8", r"G**4*R*u_0^0"],
            [r"u_4^0_9", r"P*G**4*R*u_0^0"],
            [r"u_4^0", r"P*G**4*R*u_0^0"],
            [r"u_1^1_10", r"F*u_0^0"],
            [r"u_1^1", r"F*u_0^0"],
            [r"u_2^1_12", r"F*u_1^0"],
            [r"u_2^1_13", r"R*u_1^1"],
            [r"u_2^1_14", r"G*R*u_1^1"],
            [r"u_2^1_15", r"P*G*R*u_1^1"],
            [r"u_2^1", r"F*u_1^0 + P*G*R*u_1^1 - u_2^0"],
            [r"u_3^1_17", r"F*u_2^0"],
            [r"u_3^1_18", r"R*u_2^1"],
            [r"u_3^1_19", r"G*R*u_2^1"],
            [r"u_3^1_20", r"P*G*R*u_2^1"],
            [r"u_3^1", r"F*u_2^0 + P*G*R*u_2^1 - u_3^0"],
            [r"u_4^1_22", r"F*u_3^0"],
            [r"u_4^1_23", r"R*u_3^1"],
            [r"u_4^1_24", r"G*R*u_3^1"],
            [r"u_4^1_25", r"P*G*R*u_3^1"],
            [r"u_4^1", r"F*u_3^0 + P*G*R*u_3^1 - u_4^0"],
            [r"u_2^2_26", r"F*u_1^1"],
            [r"u_2^2", r"F*u_1^1"],
            [r"u_3^2_27", r"F*u_2^1"],
            [r"u_3^2_29", r"-R*(u_2^1 - u_2^2)"],
            [r"u_3^2_30", r"-G*R*(u_2^1 - u_2^2)"],
            [r"u_3^2_31", r"-P*G*R*(u_2^1 - u_2^2)"],
            [r"u_3^2", r"F*u_2^1 - P*G*R*(u_2^1 - u_2^2)"],
            [r"u_4^2_32", r"F*u_3^1"],
            [r"u_4^2_34", r"-R*(u_3^1 - u_3^2)"],
            [r"u_4^2_35", r"-G*R*(u_3^1 - u_3^2)"],
            [r"u_4^2_36", r"-P*G*R*(u_3^1 - u_3^2)"],
            [r"u_4^2", r"F*u_3^1 - P*G*R*(u_3^1 - u_3^2)"],
            [r"u_3^3_37", r"F*u_2^2"],
            [r"u_3^3", r"F*u_2^2"],
            [r"u_4^3_38", r"F*u_3^2"],
            [r"u_4^3_40", r"-R*(u_3^2 - u_3^3)"],
            [r"u_4^3_41", r"-G*R*(u_3^2 - u_3^3)"],
            [r"u_4^3_42", r"-P*G*R*(u_3^2 - u_3^3)"],
            [r"u_4^3", r"F*u_3^2 - P*G*R*(u_3^2 - u_3^3)"],
            [r"u_4^4_43", r"F*u_3^3"],
            [r"u_4^4", r"F*u_3^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testBlockJacobiPredictorI(self):
        blockJacobi = BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=I,
            **blockOps)
        run = PintRun(blockIteration=blockJacobi, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0", r"2*u_0^0"],
            [r"u_2^0", r"2*u_0^0"],
            [r"u_3^0", r"2*u_0^0"],
            [r"u_4^0", r"2*u_0^0"],
            [r"u_1^1_1", r"\chi*u_0^0"],
            [r"u_1^1_3", r"-\phi*u_0^0"],
            [r"u_1^1_4", r"\phi_{\Delta}**(-1)*(\chi - \phi)*u_0^0"],
            [r"u_1^1", r"\phi_{\Delta}**(-1)*(\chi - \phi)*u_0^0 + 2*u_0^0"],
            [r"u_2^1", r"2*u_1^1"],
            [r"u_3^1", r"2*u_1^1"],
            [r"u_4^1", r"2*u_1^1"],
            [r"u_1^2_6", r"-\phi*(u_0^0 + u_1^1)"],
            [r"u_1^2_7", r"2*u_0^0"],
            [r"u_1^2_8", r"2*\chi*u_0^0"],
            [r"u_1^2_9", r"\phi_{\Delta}**(-1)*(2*\chi*u_0^0 - \phi*(u_0^0 + u_1^1))"],
            [r"u_1^2", r"\phi_{\Delta}**(-1)*(2*\chi*u_0^0 - \phi*(u_0^0 + u_1^1)) + 2*u_0^0"],
            [r"u_2^2_10", r"\chi*u_1^1"],
            [r"u_2^2_12", r"-\phi*u_1^1"],
            [r"u_2^2_13", r"\phi_{\Delta}**(-1)*(\chi - \phi)*u_1^1"],
            [r"u_2^2", r"\phi_{\Delta}**(-1)*(\chi - \phi)*u_1^1 + 2*u_1^1"],
            [r"u_3^2", r"2*u_2^2"],
            [r"u_4^2", r"2*u_2^2"],
            [r"u_1^3_15", r"-\phi*(u_0^0 + u_1^1 + u_1^2)"],
            [r"u_1^3_16", r"3*u_0^0"],
            [r"u_1^3_17", r"3*\chi*u_0^0"],
            [r"u_1^3_18", r"\phi_{\Delta}**(-1)*(3*\chi*u_0^0 - \phi*(u_0^0 + u_1^1 + u_1^2))"],
            [r"u_1^3", r"\phi_{\Delta}**(-1)*(3*\chi*u_0^0 - \phi*(u_0^0 + u_1^1 + u_1^2)) + 2*u_0^0"],
            [r"u_2^3_19", r"\chi*u_1^2"],
            [r"u_2^3_21", r"-\phi*u_2^2"],
            [r"u_2^3_22", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^2)"],
            [r"u_2^3", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^2) + 2*u_2^2"],
            [r"u_3^3_23", r"\chi*u_2^2"],
            [r"u_3^3_24", r"\phi_{\Delta}**(-1)*(\chi - \phi)*u_2^2"],
            [r"u_3^3", r"\phi_{\Delta}**(-1)*(\chi - \phi)*u_2^2 + 2*u_2^2"],
            [r"u_4^3", r"2*u_3^3"],
            [r"u_1^4_26", r"-\phi*(u_0^0 + u_1^1 + u_1^2 + u_1^3)"],
            [r"u_1^4_27", r"4*u_0^0"],
            [r"u_1^4_28", r"4*\chi*u_0^0"],
            [r"u_1^4_29", r"\phi_{\Delta}**(-1)*(4*\chi*u_0^0 - \phi*(u_0^0 + u_1^1 + u_1^2 + u_1^3))"],
            [r"u_1^4", r"\phi_{\Delta}**(-1)*(4*\chi*u_0^0 - \phi*(u_0^0 + u_1^1 + u_1^2 + u_1^3)) + 2*u_0^0"],
            [r"u_2^4_30", r"\chi*u_1^3"],
            [r"u_2^4_32", r"-\phi*u_2^3"],
            [r"u_2^4_33", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^3)"],
            [r"u_2^4", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^3) + 2*u_2^3"],
            [r"u_3^4_34", r"\chi*u_2^3"],
            [r"u_3^4_36", r"-\phi*u_3^3"],
            [r"u_3^4_37", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^3)"],
            [r"u_3^4", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^3) + 2*u_3^3"],
            [r"u_4^4_38", r"\chi*u_3^3"],
            [r"u_4^4_40", r"-\phi*u_4^3"],
            [r"u_4^4_41", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^3)"],
            [r"u_4^4", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^3) + 2*u_4^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testBlockJacobiNoPredictor(self):
        blockJacobi = BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=blockJacobi, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0", r"0"],
            [r"u_2^0", r"0"],
            [r"u_3^0", r"0"],
            [r"u_4^0", r"0"],
            [r"u_1^1_5", r"\chi*u_0^0"],
            [r"u_1^1_7", r"-\phi*u_1^0"],
            [r"u_1^1_8", r"\phi_{\Delta}**(-1)*(\chi*u_0^0 - \phi*u_1^0)"],
            [r"u_1^1", r"\phi_{\Delta}**(-1)*(\chi*u_0^0 - \phi*u_1^0) + 2*u_1^0"],
            [r"u_2^1_9", r"\chi*u_1^0"],
            [r"u_2^1_11", r"-\phi*u_2^0"],
            [r"u_2^1_12", r"\phi_{\Delta}**(-1)*(\chi*u_1^0 - \phi*u_2^0)"],
            [r"u_2^1", r"\phi_{\Delta}**(-1)*(\chi*u_1^0 - \phi*u_2^0) + 2*u_2^0"],
            [r"u_3^1_13", r"\chi*u_2^0"],
            [r"u_3^1_15", r"-\phi*u_3^0"],
            [r"u_3^1_16", r"\phi_{\Delta}**(-1)*(\chi*u_2^0 - \phi*u_3^0)"],
            [r"u_3^1", r"\phi_{\Delta}**(-1)*(\chi*u_2^0 - \phi*u_3^0) + 2*u_3^0"],
            [r"u_4^1_17", r"\chi*u_3^0"],
            [r"u_4^1_19", r"-\phi*u_4^0"],
            [r"u_4^1_20", r"\phi_{\Delta}**(-1)*(\chi*u_3^0 - \phi*u_4^0)"],
            [r"u_4^1", r"\phi_{\Delta}**(-1)*(\chi*u_3^0 - \phi*u_4^0) + 2*u_4^0"],
            [r"u_1^2_22", r"-\phi*(u_1^0 + u_1^1)"],
            [r"u_1^2_23", r"2*u_0^0"],
            [r"u_1^2_24", r"2*\chi*u_0^0"],
            [r"u_1^2_25", r"\phi_{\Delta}**(-1)*(2*\chi*u_0^0 - \phi*(u_1^0 + u_1^1))"],
            [r"u_1^2", r"\phi_{\Delta}**(-1)*(2*\chi*u_0^0 - \phi*(u_1^0 + u_1^1)) + 2*u_1^0"],
            [r"u_2^2_26", r"\chi*u_1^1"],
            [r"u_2^2_28", r"-\phi*u_2^1"],
            [r"u_2^2_29", r"\phi_{\Delta}**(-1)*(\chi*u_1^1 - \phi*u_2^1)"],
            [r"u_2^2", r"\phi_{\Delta}**(-1)*(\chi*u_1^1 - \phi*u_2^1) + 2*u_2^1"],
            [r"u_3^2_30", r"\chi*u_2^1"],
            [r"u_3^2_32", r"-\phi*u_3^1"],
            [r"u_3^2_33", r"\phi_{\Delta}**(-1)*(\chi*u_2^1 - \phi*u_3^1)"],
            [r"u_3^2", r"\phi_{\Delta}**(-1)*(\chi*u_2^1 - \phi*u_3^1) + 2*u_3^1"],
            [r"u_4^2_34", r"\chi*u_3^1"],
            [r"u_4^2_36", r"-\phi*u_4^1"],
            [r"u_4^2_37", r"\phi_{\Delta}**(-1)*(\chi*u_3^1 - \phi*u_4^1)"],
            [r"u_4^2", r"\phi_{\Delta}**(-1)*(\chi*u_3^1 - \phi*u_4^1) + 2*u_4^1"],
            [r"u_1^3_39", r"-\phi*(u_1^0 + u_1^1 + u_1^2)"],
            [r"u_1^3_40", r"3*u_0^0"],
            [r"u_1^3_41", r"3*\chi*u_0^0"],
            [r"u_1^3_42", r"\phi_{\Delta}**(-1)*(3*\chi*u_0^0 - \phi*(u_1^0 + u_1^1 + u_1^2))"],
            [r"u_1^3", r"\phi_{\Delta}**(-1)*(3*\chi*u_0^0 - \phi*(u_1^0 + u_1^1 + u_1^2)) + 2*u_1^0"],
            [r"u_2^3_43", r"\chi*u_1^2"],
            [r"u_2^3_45", r"-\phi*u_2^2"],
            [r"u_2^3_46", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^2)"],
            [r"u_2^3", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^2) + 2*u_2^2"],
            [r"u_3^3_47", r"\chi*u_2^2"],
            [r"u_3^3_49", r"-\phi*u_3^2"],
            [r"u_3^3_50", r"\phi_{\Delta}**(-1)*(\chi*u_2^2 - \phi*u_3^2)"],
            [r"u_3^3", r"\phi_{\Delta}**(-1)*(\chi*u_2^2 - \phi*u_3^2) + 2*u_3^2"],
            [r"u_4^3_51", r"\chi*u_3^2"],
            [r"u_4^3_53", r"-\phi*u_4^2"],
            [r"u_4^3_54", r"\phi_{\Delta}**(-1)*(\chi*u_3^2 - \phi*u_4^2)"],
            [r"u_4^3", r"\phi_{\Delta}**(-1)*(\chi*u_3^2 - \phi*u_4^2) + 2*u_4^2"],
            [r"u_1^4_56", r"-\phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3)"],
            [r"u_1^4_57", r"4*u_0^0"],
            [r"u_1^4_58", r"4*\chi*u_0^0"],
            [r"u_1^4_59", r"\phi_{\Delta}**(-1)*(4*\chi*u_0^0 - \phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3))"],
            [r"u_1^4", r"\phi_{\Delta}**(-1)*(4*\chi*u_0^0 - \phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3)) + 2*u_1^0"],
            [r"u_2^4_60", r"\chi*u_1^3"],
            [r"u_2^4_62", r"-\phi*u_2^3"],
            [r"u_2^4_63", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^3)"],
            [r"u_2^4", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^3) + 2*u_2^3"],
            [r"u_3^4_64", r"\chi*u_2^3"],
            [r"u_3^4_66", r"-\phi*u_3^3"],
            [r"u_3^4_67", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^3)"],
            [r"u_3^4", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^3) + 2*u_3^3"],
            [r"u_4^4_68", r"\chi*u_3^3"],
            [r"u_4^4_70", r"-\phi*u_4^3"],
            [r"u_4^4_71", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^3)"],
            [r"u_4^4", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^3) + 2*u_4^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testBlockJacobi(self):
        blockJacobi = BlockIteration(
            "phiD**(-1)*chi*u_{n}^k + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=phiD**(-1)*chi,
            **blockOps)
        run = PintRun(blockIteration=blockJacobi, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0_1", r"\chi*u_0^0"],
            [r"u_1^0_2", r"\phi_{\Delta}**(-1)*\chi*u_0^0"],
            [r"u_1^0", r"\phi_{\Delta}**(-1)*\chi*u_0^0"],
            [r"u_2^0_3", r"\chi*u_1^0"],
            [r"u_2^0_4", r"\phi_{\Delta}**(-1)*\chi*u_1^0"],
            [r"u_2^0", r"\phi_{\Delta}**(-1)*\chi*u_1^0"],
            [r"u_3^0_5", r"\chi*u_2^0"],
            [r"u_3^0_6", r"\phi_{\Delta}**(-1)*\chi*u_2^0"],
            [r"u_3^0", r"\phi_{\Delta}**(-1)*\chi*u_2^0"],
            [r"u_4^0_7", r"\chi*u_3^0"],
            [r"u_4^0_8", r"\phi_{\Delta}**(-1)*\chi*u_3^0"],
            [r"u_4^0", r"\phi_{\Delta}**(-1)*\chi*u_3^0"],
            [r"u_1^1_9", r"2*u_1^0"],
            [r"u_1^1_11", r"-\phi*u_1^0"],
            [r"u_1^1_12", r"-\phi_{\Delta}**(-1)*\phi*u_1^0"],
            [r"u_1^1", r"-\phi_{\Delta}**(-1)*\phi*u_1^0 + 2*u_1^0"],
            [r"u_2^1_13", r"2*u_2^0"],
            [r"u_2^1_15", r"-\phi*u_2^0"],
            [r"u_2^1_16", r"-\phi_{\Delta}**(-1)*\phi*u_2^0"],
            [r"u_2^1", r"-\phi_{\Delta}**(-1)*\phi*u_2^0 + 2*u_2^0"],
            [r"u_3^1_17", r"2*u_3^0"],
            [r"u_3^1_19", r"-\phi*u_3^0"],
            [r"u_3^1_20", r"-\phi_{\Delta}**(-1)*\phi*u_3^0"],
            [r"u_3^1", r"-\phi_{\Delta}**(-1)*\phi*u_3^0 + 2*u_3^0"],
            [r"u_4^1_21", r"2*u_4^0"],
            [r"u_4^1_23", r"-\phi*u_4^0"],
            [r"u_4^1_24", r"-\phi_{\Delta}**(-1)*\phi*u_4^0"],
            [r"u_4^1", r"-\phi_{\Delta}**(-1)*\phi*u_4^0 + 2*u_4^0"],
            [r"u_1^2_25", r"3*u_1^0"],
            [r"u_1^2_27", r"-\phi*(u_1^0 + u_1^1)"],
            [r"u_1^2_28", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1)"],
            [r"u_1^2", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1) + 3*u_1^0"],
            [r"u_2^2_29", r"\chi*u_1^1"],
            [r"u_2^2_31", r"-\phi*u_2^1"],
            [r"u_2^2_32", r"\phi_{\Delta}**(-1)*(\chi*u_1^1 - \phi*u_2^1)"],
            [r"u_2^2", r"\phi_{\Delta}**(-1)*(\chi*u_1^1 - \phi*u_2^1) + 2*u_2^1"],
            [r"u_3^2_33", r"\chi*u_2^1"],
            [r"u_3^2_35", r"-\phi*u_3^1"],
            [r"u_3^2_36", r"\phi_{\Delta}**(-1)*(\chi*u_2^1 - \phi*u_3^1)"],
            [r"u_3^2", r"\phi_{\Delta}**(-1)*(\chi*u_2^1 - \phi*u_3^1) + 2*u_3^1"],
            [r"u_4^2_37", r"\chi*u_3^1"],
            [r"u_4^2_39", r"-\phi*u_4^1"],
            [r"u_4^2_40", r"\phi_{\Delta}**(-1)*(\chi*u_3^1 - \phi*u_4^1)"],
            [r"u_4^2", r"\phi_{\Delta}**(-1)*(\chi*u_3^1 - \phi*u_4^1) + 2*u_4^1"],
            [r"u_1^3_41", r"4*u_1^0"],
            [r"u_1^3_43", r"-\phi*(u_1^0 + u_1^1 + u_1^2)"],
            [r"u_1^3_44", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1 + u_1^2)"],
            [r"u_1^3", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1 + u_1^2) + 4*u_1^0"],
            [r"u_2^3_45", r"\chi*u_1^2"],
            [r"u_2^3_47", r"-\phi*u_2^2"],
            [r"u_2^3_48", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^2)"],
            [r"u_2^3", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^2) + 2*u_2^2"],
            [r"u_3^3_49", r"\chi*u_2^2"],
            [r"u_3^3_51", r"-\phi*u_3^2"],
            [r"u_3^3_52", r"\phi_{\Delta}**(-1)*(\chi*u_2^2 - \phi*u_3^2)"],
            [r"u_3^3", r"\phi_{\Delta}**(-1)*(\chi*u_2^2 - \phi*u_3^2) + 2*u_3^2"],
            [r"u_4^3_53", r"\chi*u_3^2"],
            [r"u_4^3_55", r"-\phi*u_4^2"],
            [r"u_4^3_56", r"\phi_{\Delta}**(-1)*(\chi*u_3^2 - \phi*u_4^2)"],
            [r"u_4^3", r"\phi_{\Delta}**(-1)*(\chi*u_3^2 - \phi*u_4^2) + 2*u_4^2"],
            [r"u_1^4_57", r"5*u_1^0"],
            [r"u_1^4_59", r"-\phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3)"],
            [r"u_1^4_60", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3)"],
            [r"u_1^4", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3) + 5*u_1^0"],
            [r"u_2^4_61", r"\chi*u_1^3"],
            [r"u_2^4_63", r"-\phi*u_2^3"],
            [r"u_2^4_64", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^3)"],
            [r"u_2^4", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^3) + 2*u_2^3"],
            [r"u_3^4_65", r"\chi*u_2^3"],
            [r"u_3^4_67", r"-\phi*u_3^3"],
            [r"u_3^4_68", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^3)"],
            [r"u_3^4", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^3) + 2*u_3^3"],
            [r"u_4^4_69", r"\chi*u_3^3"],
            [r"u_4^4_71", r"-\phi*u_4^3"],
            [r"u_4^4_72", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^3)"],
            [r"u_4^4", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^3) + 2*u_4^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testApproxBlockGaussSeidelNoPredictor(self):
        approxBlockGaussSeidel = BlockIteration(
            update="phiD**(-1)*chi*u_{n}^{k+1} + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi,
            **blockOps)
        run = PintRun(blockIteration=approxBlockGaussSeidel, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0", r"0"],
            [r"u_2^0", r"0"],
            [r"u_3^0", r"0"],
            [r"u_4^0", r"0"],
            [r"u_1^1_5", r"\chi*u_0^0"],
            [r"u_1^1_7", r"-\phi*u_1^0"],
            [r"u_1^1_8", r"\phi_{\Delta}**(-1)*(\chi*u_0^0 - \phi*u_1^0)"],
            [r"u_1^1", r"\phi_{\Delta}**(-1)*(\chi*u_0^0 - \phi*u_1^0) + 2*u_1^0"],
            [r"u_2^1_9", r"\chi*u_1^1"],
            [r"u_2^1_11", r"-\phi*u_2^0"],
            [r"u_2^1_12", r"\phi_{\Delta}**(-1)*(\chi*u_1^1 - \phi*u_2^0)"],
            [r"u_2^1", r"\phi_{\Delta}**(-1)*(\chi*u_1^1 - \phi*u_2^0) + 2*u_2^0"],
            [r"u_3^1_13", r"\chi*u_2^1"],
            [r"u_3^1_15", r"-\phi*u_3^0"],
            [r"u_3^1_16", r"\phi_{\Delta}**(-1)*(\chi*u_2^1 - \phi*u_3^0)"],
            [r"u_3^1", r"\phi_{\Delta}**(-1)*(\chi*u_2^1 - \phi*u_3^0) + 2*u_3^0"],
            [r"u_4^1_17", r"\chi*u_3^1"],
            [r"u_4^1_19", r"-\phi*u_4^0"],
            [r"u_4^1_20", r"\phi_{\Delta}**(-1)*(\chi*u_3^1 - \phi*u_4^0)"],
            [r"u_4^1", r"\phi_{\Delta}**(-1)*(\chi*u_3^1 - \phi*u_4^0) + 2*u_4^0"],
            [r"u_1^2_22", r"-\phi*(u_1^0 + u_1^1)"],
            [r"u_1^2_23", r"2*u_0^0"],
            [r"u_1^2_24", r"2*\chi*u_0^0"],
            [r"u_1^2_25", r"\phi_{\Delta}**(-1)*(2*\chi*u_0^0 - \phi*(u_1^0 + u_1^1))"],
            [r"u_1^2", r"\phi_{\Delta}**(-1)*(2*\chi*u_0^0 - \phi*(u_1^0 + u_1^1)) + 2*u_1^0"],
            [r"u_2^2_26", r"\chi*u_1^2"],
            [r"u_2^2_28", r"-\phi*u_2^1"],
            [r"u_2^2_29", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^1)"],
            [r"u_2^2", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^1) + 2*u_2^1"],
            [r"u_3^2_30", r"\chi*u_2^2"],
            [r"u_3^2_32", r"-\phi*u_3^1"],
            [r"u_3^2_33", r"\phi_{\Delta}**(-1)*(\chi*u_2^2 - \phi*u_3^1)"],
            [r"u_3^2", r"\phi_{\Delta}**(-1)*(\chi*u_2^2 - \phi*u_3^1) + 2*u_3^1"],
            [r"u_4^2_34", r"\chi*u_3^2"],
            [r"u_4^2_36", r"-\phi*u_4^1"],
            [r"u_4^2_37", r"\phi_{\Delta}**(-1)*(\chi*u_3^2 - \phi*u_4^1)"],
            [r"u_4^2", r"\phi_{\Delta}**(-1)*(\chi*u_3^2 - \phi*u_4^1) + 2*u_4^1"],
            [r"u_1^3_39", r"-\phi*(u_1^0 + u_1^1 + u_1^2)"],
            [r"u_1^3_40", r"3*u_0^0"],
            [r"u_1^3_41", r"3*\chi*u_0^0"],
            [r"u_1^3_42", r"\phi_{\Delta}**(-1)*(3*\chi*u_0^0 - \phi*(u_1^0 + u_1^1 + u_1^2))"],
            [r"u_1^3", r"\phi_{\Delta}**(-1)*(3*\chi*u_0^0 - \phi*(u_1^0 + u_1^1 + u_1^2)) + 2*u_1^0"],
            [r"u_2^3_43", r"\chi*u_1^3"],
            [r"u_2^3_45", r"-\phi*u_2^2"],
            [r"u_2^3_46", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^2)"],
            [r"u_2^3", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^2) + 2*u_2^2"],
            [r"u_3^3_47", r"\chi*u_2^3"],
            [r"u_3^3_49", r"-\phi*u_3^2"],
            [r"u_3^3_50", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^2)"],
            [r"u_3^3", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^2) + 2*u_3^2"],
            [r"u_4^3_51", r"\chi*u_3^3"],
            [r"u_4^3_53", r"-\phi*u_4^2"],
            [r"u_4^3_54", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^2)"],
            [r"u_4^3", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^2) + 2*u_4^2"],
            [r"u_1^4_56", r"-\phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3)"],
            [r"u_1^4_57", r"4*u_0^0"],
            [r"u_1^4_58", r"4*\chi*u_0^0"],
            [r"u_1^4_59", r"\phi_{\Delta}**(-1)*(4*\chi*u_0^0 - \phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3))"],
            [r"u_1^4", r"\phi_{\Delta}**(-1)*(4*\chi*u_0^0 - \phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3)) + 2*u_1^0"],
            [r"u_2^4_60", r"\chi*u_1^4"],
            [r"u_2^4_62", r"-\phi*u_2^3"],
            [r"u_2^4_63", r"\phi_{\Delta}**(-1)*(\chi*u_1^4 - \phi*u_2^3)"],
            [r"u_2^4", r"\phi_{\Delta}**(-1)*(\chi*u_1^4 - \phi*u_2^3) + 2*u_2^3"],
            [r"u_3^4_64", r"\chi*u_2^4"],
            [r"u_3^4_66", r"-\phi*u_3^3"],
            [r"u_3^4_67", r"\phi_{\Delta}**(-1)*(\chi*u_2^4 - \phi*u_3^3)"],
            [r"u_3^4", r"\phi_{\Delta}**(-1)*(\chi*u_2^4 - \phi*u_3^3) + 2*u_3^3"],
            [r"u_4^4_68", r"\chi*u_3^4"],
            [r"u_4^4_70", r"-\phi*u_4^3"],
            [r"u_4^4_71", r"\phi_{\Delta}**(-1)*(\chi*u_3^4 - \phi*u_4^3)"],
            [r"u_4^4", r"\phi_{\Delta}**(-1)*(\chi*u_3^4 - \phi*u_4^3) + 2*u_4^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1

    def testApproxBlockGaussSeidel(self):
        approxBlockGaussSeidel = BlockIteration(
            update="phiD**(-1)*chi*u_{n}^{k+1} + (I-phiD**(-1)*phi)* u_{n+1}^{k}",
            propagator=phi ** (-1) * chi, predictor=phiD**(-1)*chi,
            **blockOps)
        run = PintRun(blockIteration=approxBlockGaussSeidel, nBlocks=nBlocks, kMax=[0, 4, 4, 4, 4])
        result = [
            [r"u_0^0", r"0"],
            [r"u_1^0_1", r"\chi*u_0^0"],
            [r"u_1^0_2", r"\phi_{\Delta}**(-1)*\chi*u_0^0"],
            [r"u_1^0", r"\phi_{\Delta}**(-1)*\chi*u_0^0"],
            [r"u_2^0_3", r"\chi*u_1^0"],
            [r"u_2^0_4", r"\phi_{\Delta}**(-1)*\chi*u_1^0"],
            [r"u_2^0", r"\phi_{\Delta}**(-1)*\chi*u_1^0"],
            [r"u_3^0_5", r"\chi*u_2^0"],
            [r"u_3^0_6", r"\phi_{\Delta}**(-1)*\chi*u_2^0"],
            [r"u_3^0", r"\phi_{\Delta}**(-1)*\chi*u_2^0"],
            [r"u_4^0_7", r"\chi*u_3^0"],
            [r"u_4^0_8", r"\phi_{\Delta}**(-1)*\chi*u_3^0"],
            [r"u_4^0", r"\phi_{\Delta}**(-1)*\chi*u_3^0"],
            [r"u_1^1_9", r"2*u_1^0"],
            [r"u_1^1_11", r"-\phi*u_1^0"],
            [r"u_1^1_12", r"-\phi_{\Delta}**(-1)*\phi*u_1^0"],
            [r"u_1^1", r"-\phi_{\Delta}**(-1)*\phi*u_1^0 + 2*u_1^0"],
            [r"u_2^1_13", r"\chi*u_1^1"],
            [r"u_2^1_15", r"-\phi*u_2^0"],
            [r"u_2^1_16", r"\phi_{\Delta}**(-1)*(\chi*u_1^1 - \phi*u_2^0)"],
            [r"u_2^1", r"\phi_{\Delta}**(-1)*(\chi*u_1^1 - \phi*u_2^0) + 2*u_2^0"],
            [r"u_3^1_17", r"\chi*u_2^1"],
            [r"u_3^1_19", r"-\phi*u_3^0"],
            [r"u_3^1_20", r"\phi_{\Delta}**(-1)*(\chi*u_2^1 - \phi*u_3^0)"],
            [r"u_3^1", r"\phi_{\Delta}**(-1)*(\chi*u_2^1 - \phi*u_3^0) + 2*u_3^0"],
            [r"u_4^1_21", r"\chi*u_3^1"],
            [r"u_4^1_23", r"-\phi*u_4^0"],
            [r"u_4^1_24", r"\phi_{\Delta}**(-1)*(\chi*u_3^1 - \phi*u_4^0)"],
            [r"u_4^1", r"\phi_{\Delta}**(-1)*(\chi*u_3^1 - \phi*u_4^0) + 2*u_4^0"],
            [r"u_1^2_25", r"3*u_1^0"],
            [r"u_1^2_27", r"-\phi*(u_1^0 + u_1^1)"],
            [r"u_1^2_28", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1)"],
            [r"u_1^2", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1) + 3*u_1^0"],
            [r"u_2^2_29", r"\chi*u_1^2"],
            [r"u_2^2_31", r"-\phi*u_2^1"],
            [r"u_2^2_32", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^1)"],
            [r"u_2^2", r"\phi_{\Delta}**(-1)*(\chi*u_1^2 - \phi*u_2^1) + 2*u_2^1"],
            [r"u_3^2_33", r"\chi*u_2^2"],
            [r"u_3^2_35", r"-\phi*u_3^1"],
            [r"u_3^2_36", r"\phi_{\Delta}**(-1)*(\chi*u_2^2 - \phi*u_3^1)"],
            [r"u_3^2", r"\phi_{\Delta}**(-1)*(\chi*u_2^2 - \phi*u_3^1) + 2*u_3^1"],
            [r"u_4^2_37", r"\chi*u_3^2"],
            [r"u_4^2_39", r"-\phi*u_4^1"],
            [r"u_4^2_40", r"\phi_{\Delta}**(-1)*(\chi*u_3^2 - \phi*u_4^1)"],
            [r"u_4^2", r"\phi_{\Delta}**(-1)*(\chi*u_3^2 - \phi*u_4^1) + 2*u_4^1"],
            [r"u_1^3_41", r"4*u_1^0"],
            [r"u_1^3_43", r"-\phi*(u_1^0 + u_1^1 + u_1^2)"],
            [r"u_1^3_44", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1 + u_1^2)"],
            [r"u_1^3", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1 + u_1^2) + 4*u_1^0"],
            [r"u_2^3_45", r"\chi*u_1^3"],
            [r"u_2^3_47", r"-\phi*u_2^2"],
            [r"u_2^3_48", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^2)"],
            [r"u_2^3", r"\phi_{\Delta}**(-1)*(\chi*u_1^3 - \phi*u_2^2) + 2*u_2^2"],
            [r"u_3^3_49", r"\chi*u_2^3"],
            [r"u_3^3_51", r"-\phi*u_3^2"],
            [r"u_3^3_52", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^2)"],
            [r"u_3^3", r"\phi_{\Delta}**(-1)*(\chi*u_2^3 - \phi*u_3^2) + 2*u_3^2"],
            [r"u_4^3_53", r"\chi*u_3^3"],
            [r"u_4^3_55", r"-\phi*u_4^2"],
            [r"u_4^3_56", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^2)"],
            [r"u_4^3", r"\phi_{\Delta}**(-1)*(\chi*u_3^3 - \phi*u_4^2) + 2*u_4^2"],
            [r"u_1^4_57", r"5*u_1^0"],
            [r"u_1^4_59", r"-\phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3)"],
            [r"u_1^4_60", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3)"],
            [r"u_1^4", r"-\phi_{\Delta}**(-1)*\phi*(u_1^0 + u_1^1 + u_1^2 + u_1^3) + 5*u_1^0"],
            [r"u_2^4_61", r"\chi*u_1^4"],
            [r"u_2^4_63", r"-\phi*u_2^3"],
            [r"u_2^4_64", r"\phi_{\Delta}**(-1)*(\chi*u_1^4 - \phi*u_2^3)"],
            [r"u_2^4", r"\phi_{\Delta}**(-1)*(\chi*u_1^4 - \phi*u_2^3) + 2*u_2^3"],
            [r"u_3^4_65", r"\chi*u_2^4"],
            [r"u_3^4_67", r"-\phi*u_3^3"],
            [r"u_3^4_68", r"\phi_{\Delta}**(-1)*(\chi*u_2^4 - \phi*u_3^3)"],
            [r"u_3^4", r"\phi_{\Delta}**(-1)*(\chi*u_2^4 - \phi*u_3^3) + 2*u_3^3"],
            [r"u_4^4_69", r"\chi*u_3^4"],
            [r"u_4^4_71", r"-\phi*u_4^3"],
            [r"u_4^4_72", r"\phi_{\Delta}**(-1)*(\chi*u_3^4 - \phi*u_4^3)"],
            [r"u_4^4", r"\phi_{\Delta}**(-1)*(\chi*u_3^4 - \phi*u_4^3) + 2*u_4^3"]
        ]

        i = 0
        for key, value in run.taskPool.pool.items():
            assert result[i][0] == str(key)
            assert result[i][1] == str(value.fullOP)
            i = i + 1
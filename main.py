from PintRun import PintRun
from Parareal import parareal, parareal_predictor, parareal_sc, parareal_predictor_sc


class Framework:
    def __init__(self):
        self.runs = []

    def testConfiguration(self, blockIteration, predictor, nBlocks, stop_crit):
        self.runs.append(PintRun(blockIteration=blockIteration, nBlocks=nBlocks, predictor=predictor))


a = Framework()
a.testConfiguration(blockIteration=parareal, predictor=parareal_predictor, nBlocks=4, stop_crit=10)
a.testConfiguration(blockIteration=parareal_sc, predictor=parareal_predictor_sc, nBlocks=4, stop_crit=10)

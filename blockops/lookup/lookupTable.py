import os
import pickle

from blockops.utils.checkRun import checkRunParameters, reduceRun
#from blockops import BlockIteration, PintRun

# Lookup table of all lookups that can be used
# Key : Tuple of identifying components of a block iteration
# Value : Path to the lookup
lookupTable = {
    ((0, 0), '(\\phi**(-1) - \\phi_{\\Delta}**(-1))*\\chi', (0, 1), '\\phi_{\\Delta}**(-1)*\\chi', '\\phi**(-1)*\\chi',
     '\\phi_{\\Delta}**(-1)*\\chi'): os.path.dirname(os.path.realpath(__file__)) + '/PararealPhiChi.pickle',
    ((0, 0), 'F - G', (0, 1), 'G', 'F', 'None'): os.path.dirname(
        os.path.realpath(__file__)) + '/PararealFGNoPredictor.pickle',
    ((0, 0), 'F - G', (0, 1), 'G', 'F', 'G'): os.path.dirname(os.path.realpath(__file__)) + '/PararealFG.pickle',
    ((0, 0), 'F - P*G*R', (0, 1), 'P*G*R', 'F', 'None'): os.path.dirname(
        os.path.realpath(__file__)) + '/PararealSCFGNoPredictor.pickle',
    ((0, 0), 'F - P*G*R', (0, 1), 'P*G*R', 'F', 'P*G*R'): os.path.dirname(
        os.path.realpath(__file__)) + '/testPararealSCFG.pickle',
    ((0, 0), '\\phi_{\\Delta}**(-1)*\\chi', (1, 0), '1 - \\phi_{\\Delta}**(-1)*\\phi', '\\phi**(-1)*\\chi',
     '1'): os.path.dirname(os.path.realpath(__file__)) + '/BlockJacobiPredictorI.pickle',
    ((0, 0), '\\phi_{\\Delta}**(-1)*\\chi', (1, 0), '1 - \\phi_{\\Delta}**(-1)*\\phi', '\\phi**(-1)*\\chi',
     'None'): os.path.dirname(os.path.realpath(__file__)) + '/BlockJacobiNoPredictor.pickle',
    ((0, 0), '\\phi_{\\Delta}**(-1)*\\chi', (1, 0), '1 - \\phi_{\\Delta}**(-1)*\\phi', '\\phi**(-1)*\\chi',
     '\\phi_{\\Delta}**(-1)*\\chi'): os.path.dirname(os.path.realpath(__file__)) + '/BlockJacobi.pickle',
    ((0, 1), '\\phi_{\\Delta}**(-1)*\\chi', (1, 0), '1 - \\phi_{\\Delta}**(-1)*\\phi', '\\phi**(-1)*\\chi',
     'None'): os.path.dirname(os.path.realpath(__file__)) + '/ApproxBlockGaussSeidelNoPredictor.pickle',
    ((0, 1), '\\phi_{\\Delta}**(-1)*\\chi', (1, 0), '1 - \\phi_{\\Delta}**(-1)*\\phi', '\\phi**(-1)*\\chi',
     '\\phi_{\\Delta}**(-1)*\\chi'): os.path.dirname(os.path.realpath(__file__)) + '/ApproxBlockGaussSeidel.pickle',
    ((1, 0), '(1 - T_C^F*\\tilde{\\phi}_C**(-1)*T_F^C*\\phi)*(1 - \\tilde{\\phi}**(-1)*\\phi)', (0, 1),
     'T_C^F*\\tilde{\\phi}_C**(-1)*T_F^C*\\chi', (0, 0),
     '-T_C^F*\\tilde{\\phi}_C**(-1)*T_F^C*\\phi*\\tilde{\\phi}**(-1)*\\chi + \\tilde{\\phi}**(-1)*\\chi',
     '\\phi**(-1)*\\chi', 'T_C^F*\\tilde{\\phi}_C**(-1)*T_F^C*\\chi'): os.path.dirname(
        os.path.realpath(__file__)) + '/PFASST.pickle'
}


def picklePintRun(fileName: str, run: object, blockIteration: object) -> None:
    """
    Pickles an existing PinTRun and saves it to "fileName"

    :param fileName: Where to save
    :param run: PintRun to pickle
    :param blockIteration: Associated block iteration
    """
    with open(os.path.dirname(os.path.realpath(__file__)) + '/' + fileName, "wb") as file_:
        pickle.dump(run, file_, -1)
    print('To add the block Iteration to the lookup table add the following part in the lookupTable dictionary:')
    print(createTupleFromBlockIteration(blockIteration), ':',
          'os.path.dirname(os.path.realpath(__file__))' + f"+ '/{fileName}'")


def createTupleFromBlockIteration(blockIteration: object) -> tuple:
    """
    Creates tuple from identifying settings of a BlockIteration

    :param blockIteration: Block iteration
    :return: Tuple of identifying settings
    """
    tmp = []
    for key, value in blockIteration.blockCoeffs.items():
        tmp.append(key)
        tmp.append(value.name)
    tmp.append(blockIteration.propagator.name)
    if blockIteration.predictor is not None:
        tmp.append(blockIteration.predictor.name)
    else:
        tmp.append('None')
    return tuple(tmp)


def findEntry(blockIteration: object, N: int, K: list) -> tuple:
    """
    Checks if loopup entry exists for given block iteration.
    If it exists, checks if the lookup entry computed enough iterations and blocks

    :param blockIteration: Blockiteration
    :param N: Number of blocks
    :param K: List of number of iterations per block
    :return: Found and PintRun if found
    """
    path = lookupTable.get(createTupleFromBlockIteration(blockIteration), None)

    if path is None or not os.path.isfile(path):
        return False, None

    load = pickle.load(open(path, "rb", -1))

    if not checkRunParameters(load, N, K):
        return False, None

    reduceRun(load, N, K, useCopy=False)
    return True, load

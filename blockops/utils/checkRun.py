import numpy as np
import copy

#from blockops import PintRun


def checkRunParameters(run: object, N: int, K: list) -> bool:
    """
    Check if the run has been computed for enough iterations and blocks

    :param run: PintRun to check
    :param N: Number of blocks
    :param K: List of number of iterations per block
    :return: True if check passes, else false
    """
    if N > run.nBlocks or len(K) > len(run.kMax) or np.max(np.array(K) > np.array(run.kMax)[:len(K)]):
        return False
    else:
        return True


def reduceRun(run: object, N: int, K: list, useCopy: bool = True) -> object:
    """
    Reduces an existing run to a smaller or equal number of iterations and/or blocks.
    Uses a copy if "useCopy" is True, else the object is used.

    :param run: PintRun to reduce
    :param N: Number of blocks
    :param K: List of number of iterations per block
    :param useCopy: Use a copy or work on the object
    :return: reduced PintRun
    """
    if useCopy:
        newRun = copy.deepcopy(run)  # Can be expensive
    else:
        newRun = run

    tmpBlockRules = {}
    tmpFacBlockRules = {}
    for n in range(N + 1):
        if (n, 0) in run.blockRules:
            tmpBlockRules[(n, 0)] = run.blockRules[(n, 0)]
            tmpFacBlockRules[(n, 0)] = run.facBlockRules[(n, 0)]

    for k in range(max(K)):
        for n in range(N):
            if (n + 1, k + 1) in run.blockRules:
                tmpBlockRules[(n + 1, k + 1)] = run.blockRules[(n + 1, k + 1)]
                tmpFacBlockRules[(n + 1, k + 1)] = run.facBlockRules[(n + 1, k + 1)]

    newRun.blockRules = tmpBlockRules
    newRun.facBlockRules = tmpFacBlockRules

    return newRun

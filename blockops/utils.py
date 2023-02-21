#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

def extractIndex(rest):
    """
    Function to extract upper- or lowerscript from a string containing
    a variable in latex format with double index.

    Parameters
    ----------
    rest : str
        String to extract the index from, for instance "u^{k+1}_n + ..."
        or "u_n^{k+1} - ...".

    Returns
    -------
    idx : str
        Extracted index.
    rest : str
        Rest of the string, for instance "_n + ..." or "_{k+1} - ...".
    """
    if rest.startswith('{'):
        idx = rest[1:].split('}')[0]
        rest = rest[len(idx)+3:]
    else:
        idx = rest[0]
        rest = rest[2:]
    return idx, rest


def extractTerm(s):
    """
    Extract the first block operator and its k & n dependencies from a
    given string.

    Parameters
    ----------
    s : str
        String representing the block iteration, for instance
        "(F - G) u_{n}^k + G u_{n}^{k+1}", or "G u_n^0"

    Returns
    -------
    nIndex : str
        n dependency (0 for n, 1 for n+1, ...).
    kIndex : str
        k dependency (0 for k, 1 for k+1, ...).
    blockOp : str
        String representation of the block operator.
    rest : str
        Rest of the block iteration string, "" if no block left.
    """
    # Find next u term
    idx1, idx2 = s.find('u_'), s.find('u^')
    idx = idx1 if idx2 == -1 else idx2 if idx1 == -1 else min(idx1, idx2)

    # Separate block operator
    blockOp, rest = s[:idx], s[idx+2:]
    blockOp = blockOp.strip()
    if blockOp.endswith('*'):
        blockOp = blockOp[:-1]

    # Separate indices
    nIndex, rest = extractIndex(rest)
    kIndex, rest = extractIndex(rest)
    if 'n' in kIndex:
        nIndex, kIndex = kIndex, nIndex
    nIndex = eval(nIndex.replace('n', '0'))
    kIndex = eval(kIndex.replace('k', '0'))

    return nIndex, kIndex, blockOp, rest


def getCoeffsFromFormula(s, blockOps):
    """
    Extract block coefficients from an update formula of the form
    "(F - G) u_{n}^k + G u_{n}^{k+1}", or a predictor formula like
    "G u_n^0".

    Parameters
    ----------
    s : str
        The formula to get coeffs from.
    blockOps : dict
        dictionnary containing the (irreducibles) block operators used in all
        block coefficients

    Returns
    -------
    coeffs : dict
        Keys are offset in n & k index (e.g u_{n}^{k+1} => (0, 1)), values are
        the associated BlockOperator objects.
    """
    coeffs = {}
    while s != '':
        nIndex, kIndex, block, s = extractTerm(s)
        try:
            coeffs[(nIndex, kIndex)] += eval(block, blockOps)
        except KeyError:
            coeffs[(nIndex, kIndex)] = eval(block, blockOps)
    return coeffs


def numericalOrder(nSteps, err):
    """
    Help function to compute numerical order from error and nSteps vectors 

    Parameters
    ----------
    nSteps : np.1darray
        Different number of steps to compute the error.
    err : np.1darray
        Diffenrent error values associated to the number of steps.

    Returns
    -------
    beta : float
        Order coefficient computed through linear regression.
    rmse : float
        The root mean square error of the linear regression.
    """
    x, y = np.log10(1/nSteps), np.log10(err)

    # Compute regression coefficients and rmse
    xMean = x.mean()
    yMean = y.mean()
    sX = ((x-xMean)**2).sum()
    sXY = ((x-xMean)*(y-yMean)).sum()

    beta = sXY/sX
    alpha = yMean - beta*xMean

    yHat = alpha + beta*x
    rmse = ((y-yHat)**2).sum()**0.5
    rmse /= x.size**0.5

    return beta, rmse

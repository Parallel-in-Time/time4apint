#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 17:39:24 2022

@author: cpf5546
"""

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
        "(F - G) u_{n}^k + G u_{n}^{k+1}"

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

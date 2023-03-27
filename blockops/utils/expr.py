#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 17:41:30 2023

Utility functions and classes for expression parsing and manipulation
"""
import sympy as sy
import re

Add = sy.core.add.Add
Mul = sy.core.mul.Mul
Pow = sy.core.power.Pow
Symbol = sy.core.symbol.Symbol

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


def getLeadingTerm(expr: Mul):
    """Decompose a multiplication into its leading term and the rest"""
    try:
        float(expr.args[0])

        # Leading term is a scalar
        if len(expr.args) == 2:
            # Just multiplication
            leading, rest = expr.args
        else:
            # Minus of several multiplicated terms
            leading = expr.args[1]
            rest = Mul(expr.args[0], *expr.args[2:])
    except TypeError:
        # Leading term is a operator
        leading = expr.args[0]
        rest = Mul(*expr.args[1:])

    return leading, rest

def powToMul(expr):
    """
    Convert integer powers in an expression to Muls, like a**2 => a*a.
    """
    pows = list(expr.atoms(Pow))
    if any(not e.is_Integer for b, e in (i.as_base_exp() for i in pows)):

        raise ValueError("A power contains a non-integer exponent")
    repl = zip(pows, (Mul(*[b]*e,evaluate=False) for b,e in (i.as_base_exp() for i in pows)))
    return expr.subs(repl)

def getFactorizedRule(rule, expand=True):
    dico = decomposeAddition(rule, {})
    if expand:
        expandTree(dico)
    return dico

def expandPowers(leading, rest):
    leadingMul = powToMul(leading)
    newLeading, newRest = getLeadingTerm(leadingMul)
    return newLeading, newRest*rest

def decomposeAddition(expr, dico: dict):
    """Decompose an addition into a dictionnary with leading terms as key"""
    if type(expr) == sy.Mul:
        term = expr
        leading, rest = getLeadingTerm(term)
        if type(leading) == Pow and int(leading.exp) > 1:
            leading, rest = expandPowers(leading, rest)
        try:
            dico[leading] += rest
        except KeyError:
            dico[leading] = rest
    elif type(expr) == sy.Add:
        for term in expr.args:
            if type(term) == Symbol:
                dico[term] = 1
            elif type(term) == Mul:
                leading, rest = getLeadingTerm(term)
                if type(leading) == Pow and int(leading.exp) > 1:
                    leading, rest = expandPowers(leading, rest)
                try:
                    dico[leading] += rest
                except KeyError:
                    dico[leading] = rest
            else:
                raise ValueError('got neither Symbol nor Mul')
    elif type(expr) == Symbol:
        dico[expr] = 1
    else:
        raise Exception(f'Unknown expression type {type(expr)}')
    return dico


def expandTree(dico: dict):
    """Expand an operation tree stored into a dictionnary"""
    for leading, rest in dico.items():
        if rest == 1 or type(rest) == Symbol:
            continue
        if type(rest) == Mul:
            l, r = getLeadingTerm(rest)
            if type(l) == Pow and int(l.exp) > 1:
                l, r = expandPowers(l, r)
            if type(r) == Symbol:
                dico[leading] = {l: r}
            elif type(rest) == Mul:
                subDico = {l: r}
                expandTree(subDico)
                dico[leading] = subDico
        elif type(rest) == Add:
            subDico = decomposeAddition(rest, {})
            expandTree(subDico)
            dico[leading] = subDico
        else:
            raise ValueError('got neither Add nor Mul')


def printFacto(dico: dict, tab=0):
    indent = " " * 3 * tab + "(+)"
    for key, val in dico.items():
        if type(val) == dict:
            print(f'{indent} {key} (x)')
            printFacto(val, tab + 1)
        else:
            print(f'{indent} {key} (x) {val}')
            
            
class Generator:
    def __init__(self, k, checks=2):
        self.k = k
        self.mode = 0
        self.his = []
        self.checks = checks
        self.generater = ''
        self.translate = {}

    def check(self, expr, n):
        expr_str = f'{expr}'
        unknowns = list(set(re.findall(re.compile('u_\d+\^\d+'), expr_str)))
        tmpWildcard = {}
        for i in range(len(unknowns)):
            tmp_split = re.split('_|\^', unknowns[i])
            iteration = int(tmp_split[2])
            block = int(tmp_split[1])
            tmp_block = f'n-{n - int(block)}' if n - int(block) != 0 else 'n'
            tmp_iter = f'k-{self.k - iteration}' if self.k - iteration != 0 else 'k'
            tmp_str = f'u_{tmp_block}^{tmp_iter}'
            expr_str = expr_str.replace(unknowns[i], tmp_str)
            tmpWildcard[f'x{i}'] = unknowns[i].replace('^', '\^')
            self.translate[f'x{i}'] = [n - int(block), self.k - iteration]
        self.his.append(expr_str)

        if len(self.his) >= self.checks:
            if len(set(self.his[-self.checks:])) == 1:
                self.mode = 1
                self.generater = expr
                for key, val in tmpWildcard.items():
                    self.generater = self.generater.replace(lambda expr: re.match(val, str(expr)),
                                                            lambda expr: sy.Symbol(key, commutative=False))

    def generatingExpr(self, n):
        tmp = self.generater
        for key, val in self.translate.items():
            tmp = tmp.replace(lambda expr: re.match(key, str(expr)),
                              lambda expr: sy.symbols(f'u_{n - val[0]}^{self.k - val[1]}', commutative=False))
        return tmp
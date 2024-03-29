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


def extractIndex(rest: str):
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
        rest = rest[len(idx) + 3:]
    else:
        idx = rest[0]
        rest = rest[2:]
    return idx, rest


def extractTerm(s: str):
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
    blockOp, rest = s[:idx], s[idx + 2:]
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


def getCoeffsFromFormula(s: str, blockOps: dict) -> dict:
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
    """

    Decompose a multiplication into its leading term and the rest

    Parameters
    ----------
    expr : sy.Mul
        The expression to consider

    Returns
    -------
    leading : sy.Symbol
        The leading term
    rest: sy.Mul
        The rest of the expression
    """
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


def powToMul(expr: sy.Expr) -> sy.Expr:
    """
    Converts powers in an expression to multiplications, i.e., a**2 => a*a.
    """
    pows = list(expr.atoms(Pow))
    if any(not e.is_Integer for b, e in (i.as_base_exp() for i in pows)):
        raise ValueError("A power contains a non-integer exponent")
    repl = zip(pows, (Mul(*[b] * e, evaluate=False) for b, e in (i.as_base_exp() for i in pows)))
    return expr.subs(repl)


def getFactorizedRule(rule: sy.Mul, expand: bool = True):
    """
    Factorize a rule into a dictionary

    Parameters
    ----------
    rule : sy.Mul
        The rule to factorize
    expand : bool
        Flag expanding dictionary

    Returns
    ---------
    dico: Dict
        Factorized rule as dictionary
    """
    dico = decomposeRule(rule, {})
    if expand:
        expandTree(dico)
    return dico


def expandPowers(leading, rest):
    """
    Expands "leading*rest" to "new leading * new rest" by
    writing power as multiplication.

    Parameters
    ----------
    leading : sy.Pow
        Leading term containing power
    rest : sy.Mul
        Rest of expression

    Returns
    ---------
    newLeading: sy.Symbol
        New leading term after writing power as multiplication
    newRest. sy.Mul
        New rest
    """
    leadingMul = powToMul(leading)
    newLeading, newRest = getLeadingTerm(leadingMul)
    return newLeading, newRest * rest


def decomposeRule(expr, dico: dict) -> dict:
    """
    Translate expression to dictionary representation

    Parameters
    ----------
    expr : sy.Add, sy.Mul, sy.Symbol
        Addition
    dico : dict
        Dictionary storing information about whole expression

    Returns
    ---------
    newLeading: dico
        Updated dictionary
    """
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
    """
    Expand an operation tree stored into a dictionary

    Parameters
    ----------
    dico : dict
        Dictionary to expand
    """
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
            subDico = decomposeRule(rest, {})
            expandTree(subDico)
            dico[leading] = subDico
        else:
            raise ValueError('got neither Add nor Mul')


def printFacto(dico: dict, tab: int = 0) -> None:
    """
    Prints factorized expression stored as dictionary

    Parameters
    ----------
    dico : dict
        Dictionary to print
    tab: int
        Number of tabs for printing
    """
    indent = " " * 3 * tab + "(+)"
    for key, val in dico.items():
        if type(val) == dict:
            print(f'{indent} {key} (x)')
            printFacto(val, tab + 1)
        else:
            print(f'{indent} {key} (x) {val}')


class Generator:
    """
    Helper class to generate block iterations.
    If "checks" consecutive numbers of block iterations have the same
    pattern, use this pattern to generate all following rules.
    """

    def __init__(self, k: int, checks: int = 3) -> None:
        """
        Prints factorized expression stored as dictionary

        Parameters
        ----------
        k : int
            Current iteration
        checks: int
            Number of checks before following pattern
        """
        self.k = k  # Current iteration
        self.mode = 0  # Operation mode: 0: check | 1: Pattern found
        self.his = []  # History of last block rules
        self.checks = checks  # Number of checks
        self.generater = ''  # String representing block iteration
        self.translate = {}  # Helper string to symbols

    def check(self, expr: sy.Expr, n: int):
        """
        Check if block rule of block *n* follows the
        pattern of previous block rules

        If pattern is equivalent, set mode to 1

        Parameters
        ----------
        expr : sy.Expr
            Newest rule for block n
        n: int
            Current block
        """
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

    def generatingExpr(self, n: int):
        """
        Generate expression for block *n*

        Parameters
        ----------
        n : int
            Create iteration for block n
        """
        tmp = self.generater
        for key, val in self.translate.items():
            tmp = tmp.replace(lambda expr: re.match(key, str(expr)),
                              lambda expr: sy.symbols(f'u_{n - val[0]}^{self.k - val[1]}', commutative=False))
        return tmp

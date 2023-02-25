#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 18:13:46 2023

@author: telu
"""
import sympy as sy

from blockops.problem import BlockProblem


def simplify_string(rule):
    terms = rule.args
    str_terms = []
    minus = []
    for item in terms:
        str_terms.append(str(item))
        if str_terms[-1].startswith('-'):
            str_terms[-1] = str_terms[-1][1:]
            minus.append(True)
        else:
            minus.append(False)
    indices = [[None for _ in range(len(str_terms))] for _ in range(len(str_terms))]

    for i in range(len(str_terms)):
        for j in range(len(str_terms)):
            if i == j:
                indices[i][j] = 0
            else:
                indices[i][j] = next(
                    (q for q in range(min(len(str_terms[i]), len(str_terms[j]))) if str_terms[i][q] != str_terms[j][q]),
                    None)
    maxi = [max(item) for item in indices]
    maxMatches = max(maxi)
    while maxMatches > 0:
        max_matches = [i for i, j in enumerate(maxi) if j == max(maxi)]
        new_string = str_terms[max_matches[0]][:maxMatches]
        lastChar = new_string[-1]
        save = ''
        while lastChar == '\\':
            save = new_string[-1]
            new_string = new_string[:-1]
            lastChar = new_string[-1]
        new_string += '('
        first = True
        sign = ''
        for item in max_matches:
            new_string += ('- ' if minus[item] else sign) + save + str_terms[item][maxMatches:]
            if first:
                first = False
                sign = '+'
        new_string += ')'
        str_terms = [i for j, i in enumerate(str_terms) if j not in max_matches]
        str_terms.append(new_string)
        indices = [[None for _ in range(len(str_terms))] for _ in range(len(str_terms))]

        for i in range(len(str_terms)):
            for j in range(len(str_terms)):
                if i == j:
                    indices[i][j] = 0
                else:
                    indices[i][j] = next(
                        (q for q in range(min(len(str_terms[i]), len(str_terms[j]))) if
                         str_terms[i][q] != str_terms[j][q]),
                        None)
        maxi = [max(item) for item in indices]
        maxMatches = max(maxi)
    new_rule = str_terms[0]
    for i in range(1, len(str_terms)):
        new_rule += '+' + str_terms[i]
    # q = sy.sympify(new_rule) not working
    return new_rule

# Dummy problem
prob = BlockProblem(1, 1, 3, 1, 'BE')
prob.setApprox('BE')
prob.setCoarseLevel(1)

algo = prob.getBlockIteration('PFASST')

B00 = algo.blockCoeffs[(0, 0)].symbol
B01 = algo.blockCoeffs[(0, 1)].symbol
B10 = algo.blockCoeffs[(1, 0)].symbol

u00, u01, u10 = sy.symbols('u_0^0, u_0^1, u_1^0', commutative=False)

expr = B00*u00 + B01*u01 + B10*u10
e1 = expr.expand()

new_rule = simplify_string(rule=e1)
print(f'${new_rule.replace("**","^").replace("(-1)","{-1}")}$')
c1 = algo.blockOps[r'\tilde{\phi}_C'].symbol**(-1)
c2 = algo.blockOps[r'\tilde{\phi}'].symbol**(-1)



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 25 10:49:52 2022

@author: telu
"""
import sympy as sy
import numpy as np

dico = {}
f, g = sy.symbols('f,g', commutative=False)
null = f*0

# Parameters
nBlock = 3

# Algorithm definition
# -- list of block tasks
blockOperators = [
    {"dep": (-1, -1),
     "sym": f,
     },
    {"dep": (-1, -1),
     "sym": -g,
     },
    {"dep": (-1, 0),
     "sym": g,
     }]
# -- list of maximum iteration number
kMax = np.arange(nBlock+1)
kMax = [0, 1, 2, 2]

class Task(object):

    def __init__(self, sym, dep):
        self.sym = sym
        self.dep = dep

    @property
    def output(self):
        return self.sym * self.dep

    def __add__(self, other):
        if isinstance(other, Task):
            return Task
        return Task()



# Generic part
# -- get node dependency (depends on kMax list)
def node(n, k):
    if k > kMax[n]:
        return sy.symbols(f'u_{n}^{kMax[n]}', commutative=False)
    else:
        return sy.symbols(f'u_{n}^{k}', commutative=False)

# -- build next node (depends on kMax list and tasks)
def buildNextNode(n, k):
    if k < kMax[n+1]:
        newSol = null
        for op in blockOperators:
            nMod, kMod = op['dep']
            newSol += op['sym']*node(n+1+nMod, k+1+kMod)
        newSol.simplify()
        dico[n+1, k+1] = newSol

# -- initial guess
dico[0, 0] = node(0, 0)
for n in range(nBlock):
    dico[n+1, 0] = g * node(n, 0)

# -- sweep over all block and iterations
for k in range(max(kMax)):
    for n in range(nBlock):
        buildNextNode(n, k)

# Functionnality to extract tasks from simplified block iteration

# -- conveniency class to generate sequence of names
class NameGenerator(object):

    def __init__(self, prefix):
        self.prefix = prefix
        self.counter = 0

    def get(self):
        name = f'{self.prefix}_{self.counter}'
        self.counter += 1
        return name

# -- extract task from one node
def extractTasks(node):

    tName = NameGenerator('v')
    tasks = {}

    def getTasks(node):
        if node.func in [sy.Add, sy.Mul]:
            name = tName.get()
            # Get operation and dependencies
            if node.func == sy.Add:
                op = '+'
            elif node.func == sy.Mul:
                op = 'o'
            dep = [getTasks(n) for n in node.args]
            # Some fix to merge the -1 into one given tasks
            if isinstance(dep[0], sy.core.numbers.NegativeOne):
                merged = dep[0]*dep[1]
                dep = [merged] + dep[2:]
            # Store task in dictionary
            tasks[name] = {'op': op, 'dep': dep}
        else:
            name = node
        return name

    getTasks(node)

    return tasks

tasks1 = extractTasks(dico[1, 1])
tasks2 = extractTasks(dico[3, 2])

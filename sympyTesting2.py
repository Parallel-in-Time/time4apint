#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sympy as sy

from blockops.problem import BlockProblem

# Dummy problem
prob = BlockProblem(1, 1, 3, 1, 'BE')
prob.setApprox('BE')
prob.setCoarseLevel(1)

algo = prob.getBlockIteration('PFASST')

B00 = algo.blockCoeffs[(0, 0)].symbol
B01 = algo.blockCoeffs[(0, 1)].symbol
B10 = algo.blockCoeffs[(1, 0)].symbol

u00, u01, u10 = sy.symbols('u_0^0, u_0^1, u_1^0', commutative=False)

deps = {u00, u01, u10}

expr = B00*u00 + B01*u01 + B10*u10

# Expression from which we should extract the tasks
e1 = expr.expand()

verbose = True

# -----------------------------------------------------------------------------
# Stage 1 : factorize expression into a dictionnary
# -----------------------------------------------------------------------------
    
# Utility aliases
Add = sy.core.add.Add
Mul = sy.core.mul.Mul
Pow = sy.core.power.Pow
Symbol = sy.core.symbol.Symbol

def getLeadingTerm(expr: Mul):
    """Decompose a multiplication into its leading term and the rest"""
    if expr.args[0] != -1:
        # Non-negative term
        leading = expr.args[0]
        rest = Mul(*expr.args[1:])
    else:
        # Negative term with leading -1
        if len(expr.args) == 2:  
            # Just minus one term
            leading, rest = expr.args
        else:
            # Minus of several multiplicated terms
            leading = expr.args[1]
            rest = Mul(-1, *expr.args[2:])
    return leading, rest

def decomposeAddition(expr: Add, dico: dict):
    """Decompose an addition into a dictionnary with leading terms as key"""
    for term in expr.args:
        if type(term) == Symbol:
            dico[term] = 1
        elif type(term) == Mul:
            leading, rest = getLeadingTerm(term)
            try:    
                dico[leading] += rest
            except KeyError:
                dico[leading] = rest
        else:
            raise ValueError('got neither Symbol nor Mul')
    return dico

def expandTree(dico: dict):
    """Expand an operation tree stored into a dictionnary"""
    for leading, rest in dico.items():
        if rest is None:
            continue
        if type(rest) == Mul:
            l, r = getLeadingTerm(rest)
            dico[leading] = {l: r}
        elif type(rest) == Add:
            subDico = decomposeAddition(rest, {})
            expandTree(subDico)
            dico[leading] = subDico
            
dico = decomposeAddition(e1, {})  # Note : suppose that e1 is an addition ...
expandTree(dico)
# --> end of stage 1

if verbose:
    print('Factorized dictionnary :')
    print(' -- note : (+) are additions, (x) are multiplications')
    # Helping function for printing
    def printFacto(dico: dict, tab=0):
        indent = " "*3*tab+"(+)"
        for key, val in dico.items():
            if type(val) == dict:
                print(f'{indent} {key} (x)')
                printFacto(val, tab+1)
            else:
                print(f'{indent} {key} (x) {val}')
    printFacto(dico)
    
    
# -----------------------------------------------------------------------------
# Stage 2 : generate tasks from factorized dictionnary
# -----------------------------------------------------------------------------

class Counter(object):
    """Helping class to be used as a counter (value stored in n attribute)"""
    
    def __init__(self):
        self.n = 0
        
    def increment(self):
        """Increment counter value by one"""
        self.n += 1
        
    def __str__(self):
        return str(self.n)


class TasksPool(object):
    """Helping class to store the description of the tasks"""
    
    def __init__(self):
        self.counter = Counter()
        self.tasks = {}
        self.results = {}
        
    def addTask(self, ope, inp, dep):
        """
        Add a task to the pool, considering one operator, one input, 
        and a task dependency.

        Parameters
        ----------
        ope : Symbol
            The operator used for this task.
        inp : Expression
            The input of this task (full expression).
        dep : sympy expression
            The dependencies for this task, in function of other tasks or
            block variables.

        Returns
        -------
        task : Symbol
            The symbol fo this task (T0, T1, ...).
        res : Expression
            The result of this task (full expression).
        """
        res = (ope*inp).simplify()
        if res in self.results:
            # Task already in pool
            task = self.results[res]
        elif -res in self.results:
            # Negative of the task already in pool
            task = -self.results[-res]
        else:
            # Task not in pool, create and add it
            task = sy.symbols(f'T{self.counter}', commutative=False)
            # print(task, ':', ope, '--', inp)
            self.tasks[task] = (ope, inp, dep)
            self.results[res] = task
            self.counter.increment()
            
        return task, res
            
# To store the tasks
pool = TasksPool()


def createTasks(dico: dict):
    """
    Function extracting the tasks from a factorized dictionnary

    Parameters
    ----------
    dico : dict
        Dictionnary containig a factorized expression

    Returns
    -------
    res : Expression
        Full expression for the result of the dictionnary.
    dep : Expression
        Expression for the result in function of tasks.
    """
    res = 0
    dep = 0
    for ope, inp in dico.items():
        if inp == 1:
            res = res + ope
            dep = res + ope
        if type(inp) is dict:
            t, r = pool.addTask(ope, *createTasks(inp))
            res = res + r
            dep = dep + t
        elif type(inp) is Symbol:
            t, r = pool.addTask(ope, inp, inp)
            res = res + r
            dep = dep + t
    return res, dep
             
createTasks(dico)
# --> end of stage 2

if verbose:
    print('List of tasks :')
    for task, descr in pool.tasks.items():
        print(' --', task)
        print('    -- operator :', descr[0])
        print('    -- input :', descr[1])
        print('    -- dependency :', descr[2])
        print('    -- result :', descr[0]*descr[1])

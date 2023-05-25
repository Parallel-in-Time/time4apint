import sympy as sy
import numpy as np
import copy
import sys
import re


class BlockIterationGenerator():

    def __init__(self):
        pass

    def solve(self, lhs, rhs, u):
        tmp = []
        for i in range(len(u)):
            eqn = sy.Eq(lhs[i], rhs[i])
            if rhs[i] != 0:
                q = sy.solve(eqn, u[i])
                if len(q) > 0:
                    tmp.append(q[0].simplify())
                else:
                    tmp.append(0)
            else:
                tmp.append(0)
        tmp = sy.Matrix([tmp]).transpose()
        return self.simplifyElementwise(tmp)

    def simplifyElementwise(self, q):
        return sy.Matrix([[expr.expand().simplify() for expr in q]]).transpose()

    def createVec(self, name, n, ss):
        return sy.Matrix([[ss[f'{name}_{i}'] if f'{name}_{i}' in ss
                           else sy.Symbol(f'{name}_{i}', commutative=False)
                           for i in range(1, n + 1)]]).transpose()

    def createZeros(self, n):
        return sy.zeros(n, 1)

    def jacobi(self, A, u, f, w=1):
        D = A.lower_triangular(0).upper_triangular(0)
        return self.simplifyElementwise(u + w * D.inv() * (f - A * u))

    def gausseidel(self, A, u, f, A_c, u_res):
        return self.solve(lhs=A_c * (u_res - u), rhs=f - A * u, u=u_res)

    def print_us(self, vec):
        for i in range(len(vec[0])):
            print(vec[0][i], '=')
            for j in range(len(vec[1][i].args)):
                print('       ', vec[1][i].args[j])

    def checkResults(self, u):
        gen = Generator(k=1, checks=2)
        for i in range(len(u)):
            if gen.mode == 1:
                print('Found rule: \n')
                print('u_n+1^k+1=')
                tmp = gen.generateBlockRule().args
                for i in range(len(tmp)):
                    print('   ', str(tmp[i]) if str(tmp[i]).startswith('-') or i == 0 else '+' + str(tmp[i]))
                print('')
                break
            else:
                gen.check(expr=u[i], n=i + 1)

    def generateData(self, n, L, pre_s=1, post_s=0):
        save_symbols = {}
        u_0 = sy.Symbol(r'u_0', commutative=False)
        phi = [sy.Symbol(f'\phi^{i}', commutative=False) for i in range(L)]
        chi = [sy.Symbol(f'\chi^{i}', commutative=False) for i in range(L)]
        T_c_to_f = [sy.Symbol(f'T_{i + 1}^{i}', commutative=False) for i in range(L)]
        T_f_to_c = [sy.Symbol(f'T_{i}^{i + 1}', commutative=False) for i in range(L)]
        A = [sy.Matrix(np.eye(n, dtype=int) * phi[i]) + sy.Matrix(np.eye(n, k=-1, dtype=int) * -chi[i]) for i in
             range(L)]
        u_k = [
            [self.createVec('u^0', n=n, ss=save_symbols), self.createVec('u^0', n=n, ss=save_symbols)] if i == 0 else [
                self.createVec(f'u^0_{i}', n=n, ss=save_symbols),
                self.createZeros(n)] for i in range(L)]
        u_k_1 = [
            [self.createVec('u^1', n=n, ss=save_symbols), self.createVec('u^1', n=n, ss=save_symbols)] if i == 0 else [
                self.createVec(f'u^1_{i}', n=n, ss=save_symbols),
                self.createVec(f'u^1_{i}', n=n, ss=save_symbols)] for i in
            range(L)]
        f = [sy.Matrix([[chi[0] * u_0 if i == 0 else 0 for i in range(n)]]).transpose() if i == 0 else None for i in
             range(L)]
        pre_smoothing = [pre_s for _ in range(L)]
        post_smoothing = [post_s for _ in range(L)]
        return {
            'L': L,
            'n': n,
            'phi': phi,
            'chi': chi,
            'T_c_to_f': T_c_to_f,
            'T_f_to_c': T_f_to_c,
            'A': A,
            'u_k': u_k,
            'u_k_1': u_k_1,
            'f': f,
            'pre_smoothing': pre_smoothing,
            'post_smoothing': post_smoothing,
        }


class PararealGenerator(BlockIterationGenerator):

    def __init__(self, n):
        super().__init__()
        res = self.parareal(settings=self.generateData(n=n, L=2))
        self.checkResults(res)

    def parareal(self, settings, overlapping=False):
        u = settings['u_k']
        chi = settings['chi']
        A = settings['A']
        f = settings['f']
        u_k_1 = settings['u_k_1']
        jac = self.jacobi(u=u[0][1], A=A[0], f=f[0])
        if overlapping:
            jac = self.jacobi(u=jac, A=A[0], f=f[0])
        u_k_1[0][1] = self.gausseidel(A=A[0], u=jac, f=f[0], A_c=A[1], u_res=u_k_1[0][1]).subs({chi[1]: chi[0]})
        return u_k_1[0][1]


class MultilevelGenerator(BlockIterationGenerator):
    def __init__(self, n, L, pre_smoothing=1, post_smoothing=1):
        super().__init__()
        res = self.multilevel(
            setting=self.generateData(n=n, L=L, pre_s=pre_smoothing, post_s=post_smoothing))
        self.checkResults(res)

    def multilevel(self, setting, l=0):
        L = setting['L'] - 1
        T_c_f_s = setting['T_c_to_f']
        T_f_c_s = setting['T_f_to_c']
        A = setting['A']
        u_k = setting['u_k']
        u_k_1 = setting['u_k_1']
        f = setting['f']
        pre = setting['pre_smoothing']
        post = setting['post_smoothing']
        chi = setting['chi']

        state = {}
        state2 = {}
        state3 = {}
        state4 = {}
        for i in range(L):
            state2[T_c_f_s[i] ** (-1)] = T_f_c_s[i]
            state3[chi[i + 1] * T_f_c_s[i]] = T_f_c_s[i] * chi[i]
            state4[T_f_c_s[i] * chi[i]] = chi[i + 1] * T_f_c_s[i]

        if l == L:
            u_k_1[l][1] = self.solve(lhs=A[l] * u_k_1[l][0], rhs=f[l], u=u_k_1[l][0])
        else:
            if pre[l] == 0:
                u_k_1[l][1] = copy.deepcopy(u_k[l][1])
            else:
                for i in range(pre[l]):
                    if i == 0:
                        u_k_1[l][1] = self.jacobi(u=u_k[l][1], A=A[l], f=f[l])
                    else:
                        u_k_1[l][1] = self.jacobi(u=u_k_1[l][1], A=A[l], f=f[l])
            f[l + 1] = (T_f_c_s[l] * (f[l] - A[l] * u_k_1[l][1]))
            self.multilevel(l=l + 1, setting=setting)
            tmp = self.solve(lhs=u_k_1[l][0],
                             rhs=u_k_1[l][1] + T_c_f_s[l] * u_k_1[l + 1][0],
                             u=u_k_1[l + 1][0]).subs(state2)
            for i in range(len(tmp)):
                state[u_k_1[l + 1][0][i]] = tmp[i]
            u_k_1[l][1] = self.solve(lhs=u_k_1[l][0],
                                     rhs=u_k_1[l][1] + T_c_f_s[l] * u_k_1[l + 1][1],
                                     u=u_k_1[l][0]).subs(state).expand().subs(state3).expand().subs(state4).expand()
            for i in range(post[l]):
                u_k_1[l][1] = self.jacobi(u=u_k_1[l][1], A=A[l], f=f[l])
            return u_k_1[l][1]


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
        unknowns = list(set(re.findall(re.compile('u\^\d+_\d+'), expr_str)))
        tmpWildcard = {}
        for i in range(len(unknowns)):
            tmp_split = re.split('_|\^', unknowns[i])
            iteration = int(tmp_split[1])
            block = int(tmp_split[2])
            tmp_block = f'n' if n - int(block) == 0 else f'n-{n - int(block)}'
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

    def generateBlockRule(self):
        tmp = self.generater
        for key, val in self.translate.items():
            if val[0] == 1:
                if val[1] == 1:
                    st = f'u_n^k'
                elif val[1] > 1:
                    st = 'todo'
                elif val[1] == 0:
                    st = f'u_n^k+1'
                else:
                    st = f'u_n^k'
            elif val[0] > 1:
                if val[1] == 1:
                    st = f'u_n-{val[0] - 1}^k'
                elif val[1] > 1:
                    st = 'todo'
                elif val[1] == 0:
                    st = f'u_n-{val[0] - 1}^k+1'
                else:
                    st = f'u_n-{val[0] - 1}^k'
            else:
                st = f'u_n-{val[0]}^k-{val[1]}'

            tmp = tmp.replace(lambda expr: re.match(key, str(expr)),
                              lambda expr: sy.symbols(st, commutative=False))
        return tmp


PararealGenerator(n=6)
MultilevelGenerator(n=6, L=2, pre_smoothing=1, post_smoothing=0)
MultilevelGenerator(n=6, L=3, pre_smoothing=1, post_smoothing=0)
MultilevelGenerator(n=6, L=2, pre_smoothing=2, post_smoothing=0)
MultilevelGenerator(n=6, L=2, pre_smoothing=1, post_smoothing=1)

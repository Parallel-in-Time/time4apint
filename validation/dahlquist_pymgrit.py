"""
Use PyMGRIT's routines simple_setup_problem() and Mgrit() to
generate a multigrid hierarchy and MGRIT solver and run the
solver routine mgrit.solve().
"""
import numpy as np
from pymgrit.dahlquist.dahlquist import Dahlquist
from pymgrit.core.mgrit import Mgrit

from blockops import BlockProblem

import matplotlib.pyplot as plt

nIter = 3
lam = 1j

# MGRIT run
# -- create Dahlquist's test problem with 101 time steps in the interval [0, 5]
dahlquist_lvl_0 = Dahlquist(
    t_start=0, t_stop=1, nt=41, constant_lambda=lam, method='BE')
dahlquist_lvl_1 = Dahlquist(
    t_interval=dahlquist_lvl_0.t[::2], constant_lambda=lam, method='BE')

# -- set up the MGRIT solver for the test problem
mgrit = Mgrit(
    problem=[dahlquist_lvl_0, dahlquist_lvl_1],
    tol=1e-20, max_iter=nIter, cf_iter=0)

# -- solve the test problem
info = mgrit.solve()

# -- extract fine points value (remove last time point)
uMGRIT = np.array([fPoint.value for fPoint in mgrit.u[0]])[:-1]

# BlockOps run
prob = BlockProblem(
    lam=lam, tEnd=1, nBlocks=20, scheme="RungeKutta",
    rkScheme="BE", nPoints=3)
prob.setCoarseLevel(2, tType="MGRIT")

uFine = prob.getSolution(sType="fine")[:, :-1].ravel()
tFine = prob.times[:, :-1].ravel()

algo = prob.getBlockIteration('TMG')
nNum = algo(nIter)
uBlockOps = nNum[-1, :, :-1].ravel()


plt.figure('Solution')
plt.plot(tFine, uMGRIT, 's-', markersize=12, label='pyMGRIT')
plt.plot(tFine, uBlockOps, 'o-', label='BlockOps')
plt.legend()

diff = np.linalg.norm(uMGRIT - uBlockOps, ord=np.inf)
print("Diff MGRIT-BlockOps :", diff)
diffCoarse = np.linalg.norm(uMGRIT[::2] - uBlockOps[::2], ord=np.inf)
print("Diff on coarse :", diffCoarse)


plt.figure('Fine error')
errMGRIT = np.clip(np.abs(uMGRIT-uFine), 1e-16, 10)
errBlockOps = np.clip(np.abs(uBlockOps-uFine), 1e-16, 10)
plt.semilogy(tFine, errMGRIT, 's-', label='pyMGRIT')
plt.semilogy(tFine, errBlockOps, 'o-', label='BlockOps')
plt.vlines(prob.timesCoarse[:, 0], ymin=1e-16, ymax=1, colors="gray")
plt.legend()

plt.show()

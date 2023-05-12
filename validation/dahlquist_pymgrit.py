"""
Use PyMGRIT's routines simple_setup_problem() and Mgrit() to
generate a multigrid hierarchy and MGRIT solver and run the
solver routine mgrit.solve().
"""
import numpy as np
from pymgrit.dahlquist.dahlquist import Dahlquist
from pymgrit.core.mgrit import Mgrit

import matplotlib.pyplot as plt

# Create Dahlquist's test problem with 101 time steps in the interval [0, 5]
dahlquist_lvl_0 = Dahlquist(t_start=0, t_stop=1, nt=101, constant_lambda=-1, method='BE')
dahlquist_lvl_1 = Dahlquist(t_interval=dahlquist_lvl_0.t[::2], constant_lambda=-1, method='BE')

# Set up the MGRIT solver for the test problem and set the solver tolerance to 1e-10
mgrit = Mgrit(problem=[dahlquist_lvl_0, dahlquist_lvl_1], tol=1e-10)

# Solve the test problem
info = mgrit.solve()

# Extract fine points value
a = np.array([fPoint.value for fPoint in mgrit.u[0]])

plt.plot(a)
plt.show()

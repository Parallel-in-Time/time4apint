# BlockOps application : Accuracy and stability on the complex plane

This is a base usage of the `blockops` library.
It defines a generic time-dependant problem and look at the discretization error.
This is the same approach as in the [01_discretizationError.py](../../scripts/01_discretizationError.py) script.

## Stage 1 : definition of the block problem

Uses a [S1 component](../web-components/settings.md#s1--definition-of-a-blockproblem) with `tEnd` default value set
to `tEnd=N`.

**Enabled elements after stage completion**

- compute block time-step $\Delta T = T/N$ -> `Docs` column
- display block points distribution -> `Docs` column
- display fine discretization error (and stability) with [P1 component](../web-components/plots.md#p1--contour-plot-of-error-with-stability-contour) -> `Plots` column
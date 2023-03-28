# BlockOps application : PinT performance analysis on the complex plane

This is the base usage of the `blockops` library.
It defines a generic time-dependant problem, the associated time-integrators and chose one given PinT algorithm from a list in order to analyze its performances on the complex plane.

This application is decomposed into several stages, each stages require the setting of many parameters, and allow the automatic generation of different results showing accuracy, numerical stability and performances.

## Stage 1 : definition of the block problem

Uses a [S1 component](../web-components/settings.md#s1--definition-of-a-blockproblem) with `tEnd` default value set
to `tEnd=N`.

**Enabled elements after stage completion**

- compute block time-step $\Delta T = T/N$ -> `Docs` column
- display block points distribution -> `Docs` column
- display fine discretization error (and stability) with [P1 component](../web-components/plots.md#p1--contour-plot-of-error-with-stability-contour) -> `Plots` column
- estimated fine block cost -> param column (website), must be modifiable by user


## Stage 2 : selection and analysis of a PinT algorithm

With the parameter `algo`: selected PinT algorithm, that may require those specific parameters to be set :

- `schemeApprox` : defines an approximate `BlockScheme` with eventual optional parameters using a [S3 component](../web-components/settings.md#s3--definition-of-an-approximate-blockscheme)


- `MCoarse` : define a coarse level and `BlockScheme`, using the [S4 component](../web-components/settings.md#s4--definition-of-a-coarse-blockscheme)

### List of algorithms and requirements

:hammer_and_wrench: TODO : simplify ...
    
- `Parareal` : need `schemeApprox`
- `ABGS` : need `schemeApprox`
- `ABJ` : need `schemeApprox`
- `TMG` : need `MCoarse`
- `TMG-C` : need `MCoarse` and `schemeApprox`
- `TMG-F` : need `MCoarse` and `schemeApprox`
- `PFASST`: need `MCoarse` and `schemeApprox`
- `MGRIT-FCF` : need `schemeApprox`
- ... other incoming

### Enabled elements after stage completion

:hammer_and_wrench: TODO : simplify ...

- display block iteration -> doc columns (website)
- display approximation error (and stability) with [P1 component](../web-components/plots.md#p1--contour-plot-of-error-with-stability-contour) -> `Plots` column
- display coarse error (and stability) with [P1 component](../web-components/plots.md#p1--contour-plot-of-error-with-stability-contour) -> `Plots` column
- display PinT error after (given) `K` iterationswith [P1 component](../web-components/plots.md#p1--contour-plot-of-error-with-stability-contour) -> `Plots` column
- display PinT number of iterations to discretization error with [P2 component](../web-components/plots.md#p2--contour-plot-for-number-of-iteration-to-reach-discretization-error) -> `Plots` column
- display PinT speedup & efficiency ... incoming

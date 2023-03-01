# BlockOps application : PinT performance analysis on the complex plane

This is the base usage of the `blockops` library.
It defines a generic time-dependant problem, the associated time-integrators and chose one given PinT algorithm from a list in order to analyze its 
performances on the complex plane.

This application is decomposed into two consecutive stages :

1. [Definition of the block problems](#stage-1--definition-of-the-block-problems)
2. [Selection and analysis of a PinT algorithm](#stage-2--selection-and-analysis-of-a-pint-algorithm)

Each stages require the setting of many parameters, and allow the automatic generation of different results showing accuracy, numerical stability and performances.

## Stage 1 : definition of the block problems

Done by instantiating a `BlockProblem` with specific parameters. Is decomposed in two steps :

### 1-A : Time block decomposition

Mandatory parameters :

- `N` : number of blocks $N$, strictly positive integer.
- `tEnd` : total simulation time $T$, strictly positive float. For generic analysis, current default is `tEnd=N`.

### 1-B : base (fine) block propagator

Mandatory parameters :

- `scheme` : time discretization scheme to use. See below for possible
- `M` : number of time-points per blocks $M$, strictly positive integer.

Optional parameters (given in `**schemeArgs`, non `scheme`-dependent except for default values) :

- `points` : time point distribution for each block, can be either a list of points in $[0,1]$ (ignore `M`) or a string in :
    - `EQUID` : equidistant point uniformly distributed on the block
    - `LEGENDRE` : points distribution from Legendre polynomials
    - `CHEBY-{i}` : points distribution from Chebychev polynomials of the `i`'th kind (`i in [1,2,3,4]`).
- `quadType` : quadrature type for each block, a string in :
    - `GAUSS` : don't include left and right block boundary in the points. For `points=LEGENDRE` and `points=CHEBY-{i}`, correspond to the standard Gauss nodes with those distributions. 
    For `points=EQUID`, uniformly distribute the points inside $(0,1)$.
    - `LOBATTO` : include left and right block boundary points
    - `RADAU-{LEFT,RIGHT}` : include either the left or right block boundary point (only).

- `form` : node formulation (generalized from collocation methods). 
This produce equivalent block operators, just written differently. It can be chosen from two values :
    - `Z2N` : zeros-to-nodes formulation, _i.e_ the `chi` operator produces a vector of the form $[u_0, u_0, ..., u_0]$ and `phi` represents the integration from $u_{0}$ to each block time points.
    - `N2N` : node-to-node formulation, _i.e_ the `phi` operator produces a vector of the form $[u_0, 0, ..., 0]$ and `phi` represents the 
    integration from one node to the next one.

Optional and `scheme`-dependent parameters and default values for parameters above :

- `scheme in [BE, FE, TRAP, RK2, RK4, EXACT]` : RK-type discretization
    - `nStepsPerPoint` (`int`, default=1) : number of time-steps per block time points. For instance, if `M=4` and `nStepsPerPoint=3`, then there is 12 time-steps for the whole block. Default is 1.
    - **other defaults** : `nodes=EQUID`, `quadType=RADAU-RIGHT`, `form=N2N`
- `scheme=COLLOCATION` : collocation method
    - `collUpdate` : wether to compute initial solution for next block using collocation quadrature formula, rather than an extrapolation using the Lagrange interpolating polynomial defined on the block points. Default is `False`.
    - **other defaults** : `nodes=LEGENDRE`, `quadType=RADAU-RIGHT`, `form=Z2N`

### Enabled elements after stage completion

- compute block time-step $\Delta T = T/N$ -> doc columns (website)
- display block points distribution (incoming ...) -> doc column (website)
- display fine discretization error (and stability), see [output component](2_outputs.md#c1--error-colorplot-with-stability-contour) -> output column (website)
- estimated fine block cost -> param column (website), must be modifiable by user


## Stage 2 : selection and analysis of a PinT algorithm

With the parameter `algo`: selected PinT algorithm, that may require those specific parameters to be set :

- `schemeApprox` : defines an approximate block operator with eventual optional parameters as in [stage 1-B](#1-b--base-fine-block-propagator). \
:warning: Some parameter values must be the same as for the fine propagator : `M`, `points`, `form`.

- `MCoarse` : define a coarse level using exactly the same discretization as the fine level, but with `MCoarse < M`.

### List of algorithms and requirements
    
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

- display block iteration -> doc columns (website)
- display approximation error (and stability), see [output component](2_outputs.md#c1--error-colorplot-with-stability-contour) -> output columns (website)
- display coarse error (and stability), see [output component](2_outputs.md#c1--error-colorplot-with-stability-contour) -> output columns (website)
- display PinT error after (given) `K` iterations, see [output component](2_outputs.md#c1--error-colorplot-with-stability-contour) -> output columns (website)
- display PinT number of iterations to discretization error -> output columns, see [output component](2_outputs.md#c2--colorplot-for-number-of-iteration-to-discretization-error) (website)
- display PinT speedup & efficiency, see [output component](2_outputs.md#c3--colorplot-of-speedup-and-efficiency) -> output columns (website)


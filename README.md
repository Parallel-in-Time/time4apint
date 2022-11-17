# Call of PinTy : BlockOps

## Base convention

Represent an iterative PinT algorithm with a **block iteration** of the form

```math
u_{n+1}^{k+1} = B_1^0 u_{n+1}^k + B_0^0 u_{n}^k + B_0^1 u_{n}^{k+1} + ...
```

with $B_i^j$ the **block coefficient**, built using one or a combination of **block operators** (addition, substraction, multiplication, inverse).
For instance, looking at the Parareal algorithm, we have

```math
u_{n+1}^{k+1} = (F - G) u_{n}^k + G u_{n}^{k+1},
```

with $F$ and $G$ the block operators.
Then we have two block coefficients $B_0^0 = F-G$ and $B_0^1 = G$. Note that the same block operator can be present in several block coefficients.

:warning: **Important** : block coefficients indices don't depend on $k$ and $n$, but on the offset.
Hence, $B_1^0$ is the block coefficient for the $u_{n+1}^{k+0}$ term, and the block coefficient for the $u_{n-1}^{k+1}$ term would then be $B_{-1}^{1}$.

:bell: **Note** : any combination of block operators can be seen as a unique block operator, hence a block coefficient is itself a combination of block operators and also a block operator. This aspect is fully used in the framework implementation.


## Code core concepts

1. [BlockOperator :](./doc/blockOperator.md) base object, used to represents, manipulate and evaluate block operators and block coefficients. Implemented [here](./blockops/block.py), with some documentation details provided [here](./doc/blockOperator.md).
2. [BlockIteration :](./doc/blockIteration.md) object implementing a block iteration (_i.e_ one given algorithm), using a given set of block coefficients.
Implemented [here](./blockops/iteration.py), with some documentation details provided [here](./doc/blockIteration.md).
3. [BlockProblem :](./doc/blockProblem.md) object representing a given problem, _i.e_ the numerical solution of the ODE problem represented as a linear system where each time solution is an unknown of the problem.
Implemented [here](./blockops/problem.py), with some documentation details provided [here](./doc/blockProblem.md).
4. [Task Graph:](./doc/taskGraphs.md) TODO
5. [Schedule:](./doc/schedules.md) TODO


**Important notes** :

- `BlockOperator` objects can be either symbolic or numerical block operator. Symbolic block operator only have a given cost and symbol, and can be used for speedup analysis. Numerical block operator have a cost and a matrix representation (more details [here](./doc/blockOperator.md#numerical-representation-and-evaluation)), and can be used for error and speedup analysis.
- `BlockIteration` objects depend only on `BlockOperator` objects, and are enough alone o define and analyse the speedup of a given block iteration (if relying only on symbolic `BlockOperator`)
- `BlockProblem` represent the time-integration of a Dahlquist problem on a given time interval with a given number of blocks. It defines the appropriate numerical `BlockOperator`, and can be used to generate some classical `BlockIteration` objects.

## Current testing and tutorials

- [main.py](./main.py) : some classical Block Iterations and their representation
- [testing.py](./testing.py) : some basic testing of the framework with Parareal

1. [Basic example with Parareal](./notebook/01_baseTuto.ipynb)
2. [Playing with Approximate Block Jacobi](./notebook/02_ApproximateBlockJacobi.ipynb)
3. [PLaying with Parareal, ABJ and ABGS](./notebook/03_PrimaryBlockIteration.ipynb)
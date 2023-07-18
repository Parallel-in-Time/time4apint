# Call of PinTy : BlockOps

## Motivations

Develop a python code based on a generic framework allowing to investigate and analyze the performance of iterative parallel-in-time (PinT) algorithms : [blockops](./blockops/)

In addition to this code, a website framework is provided to allow building of **Application Webpage (or WebApp)**,
that uses the [blockops] code for specific application and experiments. Currently, the website is available at
https://jupyterhub.mat.tu-harburg.de/blockops/, and here is the current list of WebApp paths :

- [Accuracy (and stability) of general time-discretization on the Complex Plane](./accuracy)
- [Automatic Generation of Task Scheduling for Parareal](./parareal)

The WebApps are currently under development : current could be improved, and other WebApp could also be added,
see the [demo WebApp](./demo) for an example.

## Base Convention

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

:bell: **Note** : block coefficients indices don't depend on $k$ and $n$, but on the offset.
Hence, $B_1^0$ is the block coefficient for the $u_{n+1}^{k+0}$ term, and the block coefficient for the $u_{n-1}^{k+1}$ term would then be $B_{-1}^{1}$.

Any combination of block operators can be seen as a unique block operator, hence a block coefficient is itself a combination of block operators and also a block operator. This aspect is fully used in the framework implementation.

## Core Concepts

> :warning: As this project is currently in continuous development, this part may be partially incomplete or outdated. Don't hesitate to use the project's [Discussions Forum](https://github.com/Parallel-in-Time/time4apint/discussions) to ask for more details.

1. [BlockOperator :](./doc/blockOperator.md) base object, used to represents, manipulate and evaluate block operators and block coefficients. Implemented [here](./blockops/block.py), with some documentation details provided [here](./doc/blockOperator.md).
2. [BlockIteration :](./doc/blockIteration.md) object implementing a block iteration (_i.e_ one given algorithm), using a given set of block coefficients.
   Implemented [here](./blockops/iteration.py), with some documentation details provided [here](./doc/blockIteration.md).
3. [BlockProblem :](./doc/blockProblem.md) object representing a given problem, _i.e_ the numerical solution of the ODE problem represented as a linear system where each time solution is an unknown of the problem.
   Implemented [here](./blockops/problem.py), with some documentation details provided [here](./doc/blockProblem.md).
4. [Task Graph:](./doc/taskGraphs.md) TODO
5. [Schedule:](./doc/schedules.md) TODO

**:scroll: Important notes** :

- `BlockOperator` objects can be either symbolic or numerical block operator. Symbolic block operator only have a given cost and symbol, and can be used for speedup analysis. Numerical block operator have a cost and a matrix representation (more details [here](./doc/blockOperator.md#numerical-representation-and-evaluation)), and can be used for error and speedup analysis.
- `BlockIteration` objects depend only on `BlockOperator` objects, and are enough alone o define and analyse the speedup of a given block iteration (if relying only on symbolic `BlockOperator`)
- `BlockProblem` represent the time-integration of a Dahlquist problem on a given time interval with a given number of blocks. It defines the appropriate numerical `BlockOperator`, and can be used to generate some classical `BlockIteration` objects.

## Project structure

### Base library :

- [blockops](./blockops/) : the main library developped for this project
- [old](./old/) : some previous implementations (:ghost: to be integrated/removed later in the current code ...)

:bell: requires at minimum Python 3.10, check [requirements.txt](./requirements.txt) for packages dependencies

### Scripts and Notebook

Those shows from basic to complexe usage example of the library. It uses relative symbolic link to the [blockops](./blockops/) directory, directly integrated in the following subdirectory, to avoid any modification of the local `PYTHONPATH` or else.

- [notebook](./notebook/) : sub-directory for Jupyter Notebook. Those are basic examples that can be used for starters.
- [scripts](./scripts/) : sub-directory for Python scripts. Those are more complex examples of use, with less documentation, mostly developped when a new functionnality is added to the `blockops` library.

Additional scripts :

- [main.py](./main.py) : some classical Block Iterations and their representation (:ghost: to be removed ...)
- [testing.py](./testing.py) : some basic testing of the framework with Parareal (:ghost: to be removed ...)
- [test_FCF.py](./test_FCF.py) : some basic testing of the framework with FCF relaxation (:ghost: to be removed ...)

## Acknowledgements

This repository results from a collaboration between University of Wuppertal
([Jens HAHNE](https://www.hpc.uni-wuppertal.de/de/mitarbeiter/jens-hahne/)) and
Hamburg University of Technology
([Thibaut LUNET](https://www.mat.tuhh.de/home/tlunet/?homepage_id=tlunet)),
as part of the [Time-X project](https://www.timex-eurohpc.eu/).

<p align="center">
  <img src="./doc/images/logo_BUW.svg" width="25%"/> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="./doc/images/tuhh-logo.png" width="30%"/> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="./doc/images/LogoTime-X.png" width="25%"/>
</p>

This project has received funding from the [European High-Performance Computing Joint Undertaking](https://eurohpc-ju.europa.eu/) (JU)
under grant agreement No 955701 ([Time-X](https://www.timex-eurohpc.eu/)).
The JU receives support from the European Union’s Horizon 2020 research and innovation programme and Belgium, France, Germany, and Switzerland.
This project also received funding from the
[German Federal Ministry of Education and Research](https://www.bmbf.de/bmbf/en/home/home_node.html) (BMBF) grant 16HPC048.

<p align="center">
  <img src="./doc/images/EuroHPC.jpg" width="35%"/> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="./doc/images/logo_eu.png" width="15%" /> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="./doc/images/BMBF_gefoerdert_2017_en.jpg" width="20%" />
</p>

## Web Interface

Install the dependencies stated in the `requirements.txt` and then open a browser at `127.0.0.1:8000` after running

```bash
python web.py
```

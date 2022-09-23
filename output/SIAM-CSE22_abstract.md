# First steps toward a generic tool for comparing parallel efficiency of iterative parallel-in-time algorithms

J. Hahne, _T. Lunet_

## Abstract 

In order to increase parallel concurrency for the simulation of time-dependent problems, many ideas for time parallelization algorithms have been developped the last two decades.
Among them, iterative parallel-in-time (PinT) methods, like Parareal, MGRIT, PFASST and Space-Time Multigrid, have received the most attention.
Since those algorithms have different variants and can depend on many parameters, there is many ways for the scientific community to use them for PinT simulations.
However, when comes the question about what is the more efficient PinT approach for a given problem, this is still rather unclear and hard to determine.

Parallel efficiency of iterative PinT algorithms relies on two main aspects : the number of iterations required to get the PinT error below an acceptable level (convergence) and the computational cost for doing all those iterations, compared to a sequential simulation without PinT (speedup).
Recently, a new analysis approach [[1]](#1) has been introduced for the convergence analysis of all iterative PinT method in a common framework, allowing to compare their convergence when using equivalent settings.
On an other side, recent research work have investigated how to compare the parallel performance of PinT methods using a common approach [[2]](#2), allowing to compare their speedup for a given number of iteration.
In this talk, we present our recent work in trying to merge both analysis (convergence & speedup), in order to develop a generic tool that can be used to compare the parallel performance of several PinT methods on simple problems, and provide indications on optimal approach for a given type of problem.

## References

<a id="1">[1]</a> 
Gander, M. J., Lunet, T., Ruprecht, D., & Speck, R. (2022). A unified analysis framework for iterative parallel-in-time algorithms. arXiv preprint arXiv:2203.16069.

<a id="2">[2]</a> 
Bolten, M., Friedhoff, S., & Hahne, J. Task Graph-Based Performance Analysis of Parallel-in-Time Methods. Available at SSRN 4201056.
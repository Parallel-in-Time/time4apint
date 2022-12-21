## Task graphs

A task graph with communication costs can be represented as a directed acyclic graph (DAG) $G=(V,E,\omega, c)$. 
Here $V = \{v_1, ..., v_n\}$ represent the set of tasks and the directed edges $E \subseteq V \times V$ represent the 
dependencies of the tasks. The weighting functions $\omega : V \rightarrow \mathbb{R}^{+}_{0}$ and $ c : E \rightarrow 
\mathbb{R}^{+}_{0}$ represent the cost of executing a task and the communication cost between two tasks, respectively.

An object of the `BlockIteration` class can automatically create the task graph for an explicit setting of the number
of blocks and the number of iterations per block. This graph can be plotted using the `plotGraph` function. Note that
the procedure described below works completely internally, so the user usually does not interact with the classes. 
 
For each time $n=1,...,N$ and each iteration $k=1...,K$, i.e. specifically $u_{n}^{k}$, a rule is created based on the 
block iteration and the initial guess $u_0^0$. This rule is simplified using existing rules and mathematical operations.
The pseudocode for the optimization looks like this:


```python
for all iterations k=1,...,K 
    for all blocks n=1,...,N
        Create rule to calculate $u_{n}^{k}$ based on $u_{0}^{0}$
        Simplify the rule based on mathematical operations and existing rules
```

The rule for a state $u_{n}^{k}$ consists similarly to a block iteration of block operators and previous states 
$u_{x}^{y}, x \leq n, y \leq k$. Tasks including their dependencies are derived from these rules and collected in a
`TaskPool. This TaskPool can be easily used to create the graph by iterating through all the tasks and adding a node 
and edges for the dependencies for each task.

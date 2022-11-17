## Task graphs

A task graph with communication costs can be represented as a directed acyclic graph (DAG) $G=(V,E,\omega, c)$. Here $V = \{v_1, ..., v_n\}$ represent the set of tasks and the directed edges $E \subseteq V \times V$ represent the dependencies of the tasks. The weighting functions $\omega : V \rightarrow \mathbb{R}^+_0$ and $c:E \rightarrow \mathbb{R}^+_0$ represent the cost of executing a task and the communication cost between two tasks, respectively.
Let $P=\{p_1,\hdots, p_{N_P}\}$ be the set of $N_P$ available processors and $A:V \rightarrow P$ be an allocation function which assigns exactly one process to each task in $V$. A schedule of a task graph is a function $S:V \rightarrow \mathbb{R}^+_0$ which assigns a start time to each task based on an allocation, subject to the following two constraints:

```math
\forall (v_i, v_j) \in E, S(v_j) \geq S(v_i) + \omega(v_i) + c(v_i, v_j)
\forall v_i, v_j \in V, v_i \neq v_j, A(v_i) = A(v_j) \Rightarrow S(v_i) \geq S(v_j)+\omega(v_j) \lor S(v_j) \geq S(v_i)+\omega(v_i)
```

The first constraint means that a task cannot be started until all its dependencies have been scheduled and executed and the data has been communicated. The second constraint means that only one task can run on a process at a time. The runtime of a schedule can then be determined by

```math
$max_{v\in V}(S(v)+\omega(v))$.
```

Under the assumptions that all communication costs are zero and $N_P = \infty $ are available, the minimum runtime of a task graph can be determined by the longest path within a DAG. Note that these two assumptions do not occur in reality, yet they yield an interesting lower runtime time bound for a given task graph.

TODO: Inclduing `TaskGraph` class
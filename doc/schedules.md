# Schedules

Let $G=(V,E,\omega, c)$ be a task graph and $P=\{p_1,..., p_{N_P}\}$ be the set of $N_P$ available processors.
Further let $A:V \rightarrow P$ be an allocation function which assigns exactly one process to each task in $V$. 
A schedule of a task graph is a function $S:V \rightarrow \mathbb{R}^+_0$ which assigns a start time to each task 
based on an allocation, subject to the following two constraints:

1) $\forall (v_i, v_j) \in E, S(v_j) \geq S(v_i) + \omega(v_i) + c(v_i, v_j) $

2) $\forall v_i, v_j \in V, v_i \neq v_j, A(v_i) = A(v_j) \Rightarrow S(v_i) \geq S(v_j)+\omega(v_j) \lor S(v_j) \geq S(v_i)+\omega(v_i)$

The first constraint implies that a task cannot be started until all its dependencies have been scheduled, executed, 
and the data has been transferred. The second constraint means that only one task can run on a process at a time. 
The runtime of a schedule can then be determined by

$$
\max_{v\in V}(S(v)+\omega(v)).
$$

Under the assumptions that all communication costs are zero and $N_P = \infty $ are available, the minimum runtime of 
a task graph can be determined by the longest path within a DAG. Note that these two assumptions do not occur in 
reality, yet they yield an interesting lower runtime time bound for a given task graph.

Currently, the following different schedules for runtime predictions are implemented:

**PinT Block-by-block**:

Iterative PinT methods typically assign the time points statically to individual processes. The most typical variant is 
given by the so-called block-by-block variant. Here all time points are distributed evenly in blocks to the processes. 
The following figure illustrates the procedure:

![Block-by-block strategy](<images/block-by-block.png>)

Based on this allocation, the schedule is based on three list:

1. ExecutableTasks: Tasks where all dependencies are fulfilled.
2. NonExecutableTasks: Tasks where some dependencies were not executed.
3. FinishedTasks: Finished tasks

Then, the typical PinT scheduling for the block-by-block strategy can be obtained by:

```
while ExecutableTasks is not empty:
    1. Select the task in ExecutableTasks with the smallest iteration index 
        and the largest block index.
    2. Determine start time based on the end times of the previous tasks and
        the availability of the processes to which this task is assigned.
    3. Update all three lists
```
The choice of the next task is important here. First, we always choose the task from the ExecutableTasks list that has
the lowest iteration index. If there are several tasks with the same iteration index, we select the task with the 
highest block index. This choice may seem unusual at first, but serves especially with multi-level strategies to make 
information available as early as possible for further processes (overlapping communication and calculations). 


**Windowing**:

The entire time domain is first divided based on the number of processes in windows, with the block-by-block basis 
then applied to each individual window. The windows are then processed sequentially, using the result of the last 
window as the initial guess of the new window. The following figure demonstrates the procedure:

![Windowing strategy](<images/windowing.png>)

Not implemented.

**Optimal**:

This scheduling produces an "optimal" scheduling, using unlimited processes and no communication costs. The scheduling 
follows a greedy strategy, where each task is immediately scheduled as soon as all its dependencies have been executed.

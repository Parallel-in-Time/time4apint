# Schedules

Currently, the following different schedules for runtime predictions are implemented:

**Block-by-block**:

Iterative PinT methods typically assign the time points statically to individual processes. The most typical variant is given by the so-called block-by-block variant. Here all time points are distributed evenly in blocks to the processes. The following figure illustrates the procedure:

![Block-by-block strategy](https://github.com/Parallel-in-Time/time4apint/tree/gaia/doc/images/block-by-block.png)

TODO: Describe scheduling

**Windowing**:

The entire time domain is first divided based on the number of processes in windows, with the block-by-block basis then applied to each individual window. The windows are then processed sequentially, using the result of the last window as the initial guess of the new window. The following figure demonstrates the procedure:

![Windowing strategy](https://github.com/Parallel-in-Time/time4apint/tree/gaia/doc/images/windowing.png)

TODO: Describe scheduling

**Optimal**:

This scheduling produces an "optimal" scheduling, using unlimited processes and no communication costs. The scheduling follows a greedy strategy, where each task is immediately scheduled as soon as all its dependencies have been executed.

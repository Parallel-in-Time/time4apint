# Current Roadmap

## Article

Choice for [Parallel Computing](https://www.sciencedirect.com/journal/parallel-computing)

- [x] Template in [output folder](./output/) (Jens)
- [ ] Check if limit of 15 pages is string or not ?
- [ ] First title and structure (Tibo)
- [ ] Test case for performance model validation
    - [ ] definition of test case
    - [ ] link with multi-modes Dahlquist analysis

## Library, Analysis

- [ ] Migration to plotly for every plots
    - [x] contours for in log scale (discretization error, PinT error)
    - [ ] contours in linear scale (nIter, speedup, efficiency)
    - [ ] 2D plots
- [ ] Code cleaning / experiments to checks every edge cases
- [ ] 3-level analysis :
    - [x] symbolic computation (Jens)
    - [ ] computation per hand for reference (Tibo)
- [ ] template for memo format
- [x] reduction of computation time for schedule (Jens)
- [ ] addition of other scheduler (bonus, Jens)
- [ ] proper definition and settings for block costs
- [ ] validation blockops
    - [x] pyMGRIT reference script with Dahlquist (Jens)
    - [ ] comparison 2-level F(CF) relaxation VS pyMGRIT
    - [ ] comparison 2-level PFASST VS pySDC

## Website

- [x] First application with time discretization accuracy / stability (Tibo)
- [ ] Second application with cost and schedule (Jens)

# Additional Ideas

## Compare PinT efficiency

- Script to plot the speedup/efficiency in function of lambda*dt on the with one given lambda value (1D)
- Choose T and nProcs, with fixed discretization error (dt fine), and compute speedup for different block size (with restard and windowing ...)

# Application outputs : PinT performance analysis on the complex plane

## Global parameters for all components

- `nVals` : number of lambda values to display in each direction of the complex plane (_i.e_ looks at `nVals*nVals` Dahlquist problems). Default is 500.
- `reLamBounds`, `imLamBounds` : bounds for the lambda real and imaginary lambda values. Default is (-4, 0.5) and (-3, 3).

## C1 : error colorplot with stability contour

Plot the error on the complex plane, in log scale, from the numerical solution obtained with one given time-integration (fine, approax, coarse, PinT, ...), versus one given reference (fine or exact).

Parameters :

- `eMin`, `eMax` : min. and max. error exponent for the contour plot, _i.e_ error is plotted between $10^{eMin}$ and $10^{eMax}$. Default is (-7, 0).


## C2 : colorplot for number of iteration to discretization error

Plot how much iteration are required fo each lambda in the complex plane such that the maximum PinT error (PinT vs fine) algorithm on each block is lower than the discretization error (fine vs exact)

Parameters :

- `nIterMax` : max. number of iterations to plot

## C3 : colorplot of speedup and efficiency

.. incoming ..


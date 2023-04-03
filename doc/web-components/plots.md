# Components for the `Plots` column in application pages

Generic description of the `Plots` components. Inputs are the main computed values require to generate the plot. Parameters are additional settings that have pre-set default values.

## P1 : contour plot of error with stability contour

Plot the error on a rectangular domain of the complex plane, in log scale, from the numerical solution obtained with one given time-integration (fine, approax, coarse, PinT, ...), versus one given reference (fine or exact).

### Inputs

- `err` : a 2D array containing error value for each lambda values
- `stab` (optional) : a 2D array containing amplification factor for each lambda values

### Parameters

- `nVals` : number of lambda values to display in each direction of the complex plane (_i.e_ looks at `nVals*nVals` Dahlquist problems). Default is 500.
- `reLamBounds`, `imLamBounds` : bounds for the lambda real and imaginary lambda values. Default is (-4, 0.5) and (-3, 3).
- `eMin`, `eMax` : min. and max. error exponent for the contour plot, _i.e_ error is plotted between $10^{eMin}$ and $10^{eMax}$. Default is (-7, 0).

## P2 : contour plot for number of iteration to reach discretization error

Plot how much iteration are required for each lambda in  the complex plane such that the maximum PinT error (PinT VS fine) algorithm on each block is lower than the discretization error (fine VS exact).

### Inputs

- `nIter` : a 2D array containing integer values for each lambda values

### Parameters

- `nVals` : number of lambda values to display in each direction of the complex plane (_i.e_ looks at `nVals*nVals` Dahlquist problems). Default is 500.
- `reLamBounds`, `imLamBounds` : bounds for the lambda real and imaginary lambda values. Default is (-4, 0.5) and (-3, 3).

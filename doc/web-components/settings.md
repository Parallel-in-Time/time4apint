# Components for the `Settings` column in application pages



## S1 : Definition of a `BlockProblem`

This component is decomposed into main stages. First, the user should define

- `lam` : the value(s) for lambda
- `tEnd` : total simulation time $T$
- `nBlocks` : number of blocks $N$ for the global problem
- `u0` : the initial solution (default=1)
- `scheme` : the chosen `BlockScheme` for fine level (see the `BlockProblem.PARAMS['scheme'].choices` for possible choices)

Once `scheme` is selected, then it displays an [S2 component](#s2--definition-of-a-blockscheme) and instantiate the `BlockProblem` object
with the `schemeArgs` given in output from `S2`.

| Input | Output |
| :---: | :----: |
| None  | `BlockProblem` object |



## S2 : Definition of a `BlockScheme`

This component set the parameters for a `BlockScheme` subclass defined by a `scheme` string parameter (value in `BlockProblem.PARAMS['scheme'].choices`). 
See `blockops.scheme.SCHEMES[scheme].PARAMS` for a list of parameters for each subclasses.
Then it returns all this parameters in a `schemeArgs` dictionary, that could be used later to instantiate a `BlockScheme` class.


| Input | Output |
| :---: | :----: |
| `scheme` string  | `schemeArgs` dict |



## S3 : Definition of an approximate `BlockScheme`

:warning: It should use the same parameter values as for the fine `BlockScheme` defined in Stage 1 (those are defined in `blockops.scheme.BlockScheme.PARAMS`). 

TODO ...


## S4 : Definition of a coarse `BlockScheme`

TODO ...

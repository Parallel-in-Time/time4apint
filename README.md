# Call of PinTy : BlockOps

## Base convention

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

:warning: **Important** : block coefficients indices don't depend on $k$ and $n$, but on the offset. 
Hence, $B_1^0$ is the block coefficient for the $u_{n+1}^{k+0}$ term, and the block coefficient for the $u_{n-1}^{k+1}$ term would then be $B_{-1}^{1}$.

:bell: **Note** : any combination of block operators can be seen as a unique block operator, which applies also to a block coefficient. This aspect is fully used in the framework implementation.


## Code core concept

A block iteration is represented using the following classes :

```python
class BlockOperator(object):
    # Attributes
    symbol      # sympy symbol (using name attribute for variable name)
    matrix      # numpy array that represent the action of this block operator on a vector
    cost        # some theoretical cost for the evaluation of this component
    components  # Dictionnary with key = name, value = BlockOperator, storing all irreducible block operator

class BlockIteration(object):
    # Attributes
    blockCoeffs  # Dictionnary with key = (n, k), value = BlockCoefficients for the update formula
    predBlockCoeffs  # Dictionnary with key = (n, k), value = BlockCoefficients for the predictor formula
    rules        # Dictionnary with numpy expression as key and values, that are supposed to be equals.
```

Arithmetic operation are oveloaded for BlockOperator, such that the BlockOperator class can represent one irreducible block operator, but also any combination of several block operators.

## Tutorials

1. [Basic example with Parareal](./notebook/01_baseTuto.ipynb)
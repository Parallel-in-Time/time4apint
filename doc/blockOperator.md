# Block Operator representation

We distinguish two types of operator :

- _irreducible_ : one elementary block operator, that cannot be decomposed into a product, addition, etc ... of other block operators. For instance, `F` and `G` in Parareal. 
- _composite_ : built from the multiplication, addition, etc ... of several block operators. For instance, `F-G` in the Parareal iteration.

Both types are represented by the following class :

```python
class BlockOperator(object):
    # Attributes used for representation and performance analysis
    symbol      # sympy symbol
    cost        # real number
    components  # dictionnary

    # Attributes used for evaluation and error analysis
    matrix      # numpy 2D array
    invert      # numpy 2D array
```

- `symbol` : is a symbolic representation of the operator, used for representation and performance analysis. For composite block operators, it becomes a sympy expression that can be broken down into symbolic operations and symbols.
- `cost` : is a theoretical cost for this operator. It is relevant only for irreducible block operators, and is `None` for any composite block operator,
- `components` : a dictionnary with `key=name` and `value=BlockOperator` containing all irreducible block operators composing the block operator. For an irreducible block operator, it only contains a reference to itself.

## Numerical representation and evaluation

For any vector $u$, its evaluation by a block operator is represented by :

```math
u_{eval} = A B^{-1} u
```

where $A$ and $B$ are square matrices, with $B$ supposed to ne invertible. This allows to inverse some operator, and avoid computing the inverse of $B$ for evaluation.
Instead, evaluation is performed in two stages :

- Solve $By=u$ using `numpy.linalg.solve` (better numerical accuracy),
- Compute evaluated solution $u_{eval} = Ay$ using `numpy.dot` matrix-vector product.

The $A$ matrix is stored in the `matrix` attribute, while the `invert` attribute stores the $B$ matrix.
When a block operator does not have an implicit part (only $A$), then the `invert` attribute is set to `None`, and vice-versa.
By default, when both `invert` and `matrix` are set to `None`, it means that the `BlockOperator` represent the identity.

Arithmetic operation between block operator are allowed, and their `matrix` and `invert` attributes are modified accordingly.

:bell: For now, addition and substraction between `BlockOperators` having an `invert` attribute not set to `None` is not allowed.
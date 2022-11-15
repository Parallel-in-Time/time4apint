# Block Iteration representation

```python
class BlockIteration(object):
    # Attributes
    name         # Name of the block iteration (default to None)
    blockCoeffs  # Dictionnary with key = (n, k), value = BlockCoefficients for the update formula
    propagator   # BlockOperator for the (fine) propagator on one block (required)
    predictor    # BlockOperator for the (coarse) predictor on one block (optional)
    rules        # Dictionnary with numpy expression as key and values, that are supposed to be equals.

    # Informational attributes
    blockOps     # Dictionnary containing the block operators
    update       # String of the update formula
```
# Block Iteration representation

```python
class BlockIteration(object):
    # Attributes
    blockCoeffs  # Dictionnary with key = (n, k), value = BlockCoefficients for the update formula
    predBlockCoeffs  # Dictionnary with key = (n, k), value = BlockCoefficients for the predictor formula
    rules        # Dictionnary with numpy expression as key and values, that are supposed to be equals.
```
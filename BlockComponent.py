import sympy as sy


class BlockComponent:
    def __init__(self, name, cost, matrix):
        self.name = name
        self._symbol = sy.symbols(self.name, commutative=False)
        self.cost = cost
        self.matrix = matrix

    def evaluateMatrix(self, timestep):
        return timestep * self.matrix

    @property
    def symbol(self):
        return self._symbol

    def __mul__(self, other):
        tmp = BlockComponent(
            name=self.name + '*' + other.name,
            cost=self.cost + other.cost,
            matrix=self.matrix)
        tmp._symbol = self._symbol * other._symbol
        return tmp

import sympy as sy


class BlockComponent:
    def __init__(self, name, cost, matrix):
        self.name = name
        self.symbol = sy.symbols(self.name, commutative=False)
        self.cost = cost
        self.matrix = matrix

    def evaluateMatrix(self, timestep):
        return timestep * self.matrix

    def getSymbol(self):
        return self.symbol

    def __mul__(self, other):
        tmp = BlockComponent(name=self.name + '*' + other.name, cost=self.cost + other.cost, matrix=self.matrix)
        tmp.symbol = self.symbol * other.symbol
        return tmp

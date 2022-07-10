import sympy as sy


class NameGenerator(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.counter = 0

    def get(self):
        if self.counter > 0:
            name = sy.symbols(f'{self.prefix}_{self.counter}', commutative=False)
        else:
            name = sy.symbols(f'{self.prefix}', commutative=False)
        self.counter += 1
        return name

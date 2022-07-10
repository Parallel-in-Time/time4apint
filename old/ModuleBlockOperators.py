import sympy as sy


class BlockOperators():
    def __init__(self, variant):
        self.f, self.g, self.r, self.p = sy.symbols('f,g, r,p', commutative=False)
        if variant == 'parareal':
            self.blockOperators = [
                {"dep": (-1, -1),
                 "sym": self.f,
                 },
                {"dep": (-1, -1),
                 "sym": -self.g,
                 },
                {"dep": (-1, 0),
                 "sym": self.g,
                 }]
        elif variant == 'parareal_spatial_coarsening':
            self.blockOperators = [
                {"dep": (-1, -1),
                 "sym": self.f,
                 },
                {"dep": (-1, -1),
                 "sym": -self.p * self.g * self.r,
                 },
                {"dep": (-1, 0),
                 "sym": self.p * self.g * self.r,
                 }]
        else:
            raise Exception('not implemented')

    def getBlockOperator(self):
        return self.blockOperators


def getBlockOperators():
    f, g, r, p = sy.symbols('f,g, r,p', commutative=False)
    # blockOperators = [
    #     {"dep": (-1, -1),
    #      "sym": f,
    #      },
    #     {"dep": (-1, -1),
    #      "sym": -p * g * r,
    #      },
    #     {"dep": (-1, 0),
    #      "sym": p * g * r,
    #      }]
    blockOperators = [
        {"dep": (-1, -1),
         "sym": f,
         },
        {"dep": (-1, -1),
         "sym": -g,
         },
        {"dep": (-1, 0),
         "sym": g,
         }]
    return blockOperators

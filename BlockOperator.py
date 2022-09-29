from BlockComponent import BlockComponent


class BlockOperator:

    SIGN = {
        '+': lambda x: +x,
        '-': lambda x: -x,
    }
    # TODO : not sure a minus sign is possible, to check later ...

    def __init__(self, blockComponent: BlockComponent, depTime: int,
                 depIter: int, sign: str):
        if sign not in self.SIGN.keys():
            raise ValueError(
                f'Unknown sign {sign}, must be in {self.SIGN.keys()}')

        self.blockComponent = blockComponent
        self.depTime = depTime
        self.depIter = depIter
        self.sign = sign
        self.sign_func = self.SIGN.get(self.sign)
        self.symbol = self.sign_func(self.blockComponent.symbol)

    # TODO : not so found of getter and setter in Python, since everything is
    #        public. It mostly add more code at then end ...
    def getDepTime(self):
        return self.depTime

    def getDepIter(self):
        return self.depIter

    def getSymbol(self):
        return self.symbol

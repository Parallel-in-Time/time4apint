from BlockComponent import BlockComponent


class BlockOperator:

    SIGN = {
        '+': lambda x: +x,
        '-': lambda x: -x,
    }

    def __init__(self, blockComponent: BlockComponent, depTime: int, depIter: int, sign: str):
        if sign not in self.SIGN.keys():
            raise ValueError(
                f'Unknown sign {sign}, must be in {self.SIGN.keys()}')

        self.blockComponent = blockComponent
        self.depTime = depTime
        self.depIter = depIter
        self.sign = sign
        self.sign_func = {
            '+': lambda x: +x,
            '-': lambda x: -x,
        }.get(self.sign)
        self.symbol = self.sign_func(self.blockComponent.symbol)

    def getDepTime(self):
        return self.depTime

    def getDepIter(self):
        return self.depIter

    def getSymbol(self):
        return self.symbol

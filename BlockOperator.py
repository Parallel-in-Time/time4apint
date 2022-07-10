from BlockComponent import BlockComponent


class BlockOperator:
    def __init__(self, blockComponent: BlockComponent, depTime: int, depIter: int, sign: str):
        if sign not in ['+', '-']:
            raise Exception('Please specify the sign of the BlockOperator as "+" or "-"')

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

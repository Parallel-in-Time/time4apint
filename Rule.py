class Rule:

    OP_FUNC = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / float(y),
        '^': lambda x, y: x ** y}

    def __init__(self, blockOperator1, op, blockOperator2, result):
        if op not in self.OP_FUNC.keys():
            raise ValueError(
                f'Unknown operation {op}, must be in {self.OP_FUNC.keys()}')

        self.blockOperator1 = blockOperator1
        self.blockOperator2 = blockOperator2
        self.op = op
        self.result = result
        self.op_func = self.OP_FUNC.get(self.op)
        self.rule = {self.op_func(self.blockOperator1.symbol,
                                  self.blockOperator2.symbol): self.result}

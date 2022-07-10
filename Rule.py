class Rule:
    def __init__(self, blockOperator1, op, blockOperator2, result):
        if op not in ['+', '-', '*', '/', '^']:
            raise Exception('Unknown operation')

        self.blockOperator1 = blockOperator1
        self.blockOperator2 = blockOperator2
        self.op = op
        self.result = result
        self.op_func = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / float(y),
            '^': lambda x, y: x ** y}.get(self.op)
        self.rule = {self.op_func(self.blockOperator1.getSymbol(), self.blockOperator2.getSymbol()): self.result}

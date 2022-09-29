from BlockOperator import BlockOperator
from Rule import Rule


class BlockIteration:
    def __init__(self, blockOperators: list, rules=None):

        if rules is None:
            rules = []

        if not isinstance(blockOperators, list) \
            or any(not isinstance(i, BlockOperator) for i in blockOperators):
            raise Exception(
                'Parameter blockOperators expects list of BlockOperator')
        if not isinstance(rules, list) \
            or any(not isinstance(i, Rule) for i in rules):
            raise Exception('Parameter rules expects list of Rules')

        self.iterationOperators = blockOperators
        self.rules = {}
        for item in rules:
            for key, value in item.rule.items():
                self.rules[key] = value

    def getOperators(self):
        return self.iterationOperators

    def getRules(self):
        return self.rules

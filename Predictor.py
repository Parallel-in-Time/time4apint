from BlockOperator import BlockOperator
from Rule import Rule


class Predictor:
    def __init__(self, predictionOperators: list, rules=None):
        if rules is None:
            rules = []
        if not isinstance(predictionOperators, list) or any(
                not isinstance(i, BlockOperator) for i in predictionOperators):
            raise ValueError('Parameter blockOperators expects list of BlockOperator')
        if not isinstance(rules, list) or any(not isinstance(i, Rule) for i in rules):
            raise ValueError('Parameter rules expects list of Rules')

        self.predictionOperators = predictionOperators
        self.rules = rules

    def getOperators(self):
        return self.predictionOperators

    def getRules(self):
        return self.rules

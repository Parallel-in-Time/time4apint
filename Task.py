import sympy as sy


class Task(object):
    def __init__(self, op, res, cost):
        self.op = op  # Operation (sympy expression)
        self.res = res  # Result (what is computed by this task)
        self.dep = self.find_dependencies()  # Find dependencies based on op
        # Set a name (only for visualization)
        if len(op.args) > 0:
            self.name = op.args[0]
        else:
            self.name = 'copy'
        self.cost = cost

    def find_dependencies(self):
        """
        Gets the dependencies from the operation (expects dependencies to start with u)

        :return: dependencies
        """
        return [item for item in self.op.atoms() if (isinstance(item, sy.Symbol) and item.name.startswith('u'))]

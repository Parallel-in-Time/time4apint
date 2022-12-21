import re

import sympy as sy

COLOR_LIST = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974',
              '#64b5cd']


class TaskPool:
    def __init__(self):
        self.pool = {}
        self.colorLookup = {}
        self.colorCounter = 0

    def addTask(self, operation, result, cost):
        tmp = Task(op=operation, result=result, cost=cost, taskpool=self)
        for item in tmp.dep:
            self.pool[item].followingTasks.append(result)
        tmp.color = self.getColor(name=tmp.name)
        self.pool[result] = tmp

    def getTask(self, name):
        return self.pool[name]

    def getColor(self, name):
        if re.match(r"\$u_\d\^\d|u\^\d_\d", name):
            name = "u_*^*"
        if name in self.colorLookup:
            return self.colorLookup[name]
        else:
            color = 'gray'
            if self.colorCounter < len(COLOR_LIST):
                color = COLOR_LIST[self.colorCounter]
                self.colorLookup[name] = color
                self.colorCounter += 1
            self.colorLookup[name] = color
            return color


class Task(object):
    """Represents one task"""

    def __init__(self, op, result, cost, taskpool):
        """
        Creates a task based.

        Parameters
        ----------
        op : TYPE
            DESCRIPTION. Represents the expression that the task performs.
        result : TYPE
            DESCRIPTION. A representation for the result of the expression
        cost : TYPE
            DESCRIPTION. The cost of the task
        """
        self.op = op  # Operation (sympy expression)
        self.result = result  # Result (what is computed by this task)
        self.cost = cost
        self.color = "gray"
        self.result_latex = self.translateToLatex(input=f'{result}')
        if len(re.split('_|\^', result.name)) == 3:
            self.type = 'main'
        else:
            self.type = 'sub'
        if len(re.split('_|\^', result.name)) >= 3:
            self.iteration = int(re.split('_|\^', result.name)[2])
            self.block = int(re.split('_|\^', result.name)[1])
        else:
            raise Exception("This should not happen")
        if f'{op}' != '0':
            self.op_latex = self.translateLatexOp(op=f'{op}')
        else:
            self.op_latex = 'initial condition'
        self.dep = self.findDependencies()  # Find dependencies based on op
        self.name = self.computeName()
        pattern = re.compile(str(result).replace('^', '\^') + "_\d$")
        self.subtasks = [key for key in taskpool.pool if pattern.match(str(key))]
        self.followingTasks = []

    def findDependencies(self):
        """
        Gets the dependencies from the operation (expects dependencies to start with u)

        :return: dependencies
        """
        tmp = [item for item in self.op.atoms() if (isinstance(item, sy.Symbol) and item.name.startswith('u'))]
        return tmp

    # TODO: Find a better way to set the name
    def computeName(self):
        name = ''
        if len(self.op.args) > 0:
            if isinstance(self.op.args[0], sy.Symbol):
                if len(re.split('u_|u\^', self.op.args[0].name)) > 1:
                    name = re.sub('\$', '', f'{self.result}')
                    name = f"${name}$"
                else:
                    name = re.sub('\$', '', f'{self.op.args[0]}')
                    name = f"${name}$"
            elif isinstance(self.op.args[0], sy.Integer):
                func = self.op.func
                if self.op.func.is_Mul:
                    func = '*'
                elif self.op.func.is_Add:
                    func = '+'
                else:
                    raise Exception(f'Unknown func in {self.result}={self.op} with {type(self.op.func)}')
                name = f'{self.op.args[0]}{func}'
            elif isinstance(self.op.args[0], sy.Pow):
                name = f'{self.op.args[0].args[0]}^{{{self.op.args[0].args[1]}}}'
                name = re.sub('\$', '', f'{name}')
                name = f"${name}$"
            else:
                raise Exception(f'Unknown operation in {self.result}={self.op} with {type(self.op.args[0])}')
        else:
            name = re.sub('\$', '', f'{self.result.name}')
            name = f"${name}$"
        return name

    def translateToLatex(self, input):
        indices = re.split('_|\^', input)
        st = ''
        for i in range(3, len(indices)):
            if i == 3:
                st += f'{indices[i]}'
            else:
                st += f',{indices[i]}'
        if len(indices) > 3:
            new_string = f'${{{indices[0]}_{indices[1]}^{indices[2]}|}}_{{{st}}}$'
        else:
            new_string = f'${{{indices[0]}_{indices[1]}^{indices[2]}}}$'
        return new_string

    def translateLatexOp(self, op):
        a = re.search('u_\d+\^\d+(_\d+)*', f'{op}')
        u_part = self.translateToLatex(input=a.group(0))
        rest = re.sub('u_\d+\^\d+(_\d+)*', '', f'{op}')
        rest += u_part
        rest = re.sub('\$', '', f'{rest}')
        rest = f'${rest}$'
        return rest

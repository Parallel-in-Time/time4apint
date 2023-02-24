import re

import sympy as sy

COLOR_LIST = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974',
              '#64b5cd', '#818d6d', '#7f0c17', '#c4ddb2', '#2ab414', '#f98131', '#08786d', '#142840',
              '#d065b5''#a73307']


class TaskPool:
    def __init__(self):
        self.pool = {}
        self.colorLookup = {'$IC$': 'lightgrey'}
        self.colorCounter = 0
        self.unassignedSubtasks = []

    def addTask(self, operation, result, cost):
        tmp = Task(op=operation, result=result, cost=cost, taskpool=self)
        for item in tmp.dep:
            self.pool[item].followingTasks.append(result)
        tmp.color = self.getColor(type=tmp.opType)
        self.pool[result] = tmp

    def getTask(self, name):
        return self.pool[name]

    def getColor(self, type):
        if type in self.colorLookup:
            return self.colorLookup[type]
        else:
            color = 'gray'
            if self.colorCounter < len(COLOR_LIST):
                color = COLOR_LIST[self.colorCounter]
                self.colorLookup[type] = color
                self.colorCounter += 1
            self.colorLookup[type] = color
            return color

    def nextTask(self, task, list):
        next_task = self.getTask(task)
        if len(next_task.followingTasks) == 1 and len(next_task.dep) == 1 and next_task.type == 'sub':
            list.append(task)
            list = self.nextTask(next_task.followingTasks[0], list=list)
            return list
        else:
            return list

    def combineTasks(self, listOfTasks):

        # Assemble all tasks to combine
        tmp = []
        for task in listOfTasks:
            tmp.append(self.getTask(task))

        # Combine operation and cost of all tasks
        op = tmp[-1].op
        cost = tmp[-1].cost
        for i in range(len(tmp) - 2, -1, -1):
            op = op.subs({tmp[i].result: tmp[i].op})
            cost += tmp[i].cost

        # Updating pool - removing combined tasks from followingTasks lists
        for d in tmp[0].dep:
            for i in range(len(self.pool[d].followingTasks)):
                if self.pool[d].followingTasks[i] == tmp[0].result:
                    self.pool[d].followingTasks[i] = tmp[-1].result
                    break

        # Updating pool - removing combined tasks from subtasks
        a = 3
        for q in tmp[:-1]:
            self.pool[q.parent].subtasks = [item for item in self.pool[q.parent].subtasks if item != q.result]

        # Update the last cast which now represents all combined tasks
        tmp[-1].updateTask(op=op, cost=cost, taskpool=self)

        # Remove all but the updated task from the pool
        for i in range(0, len(listOfTasks) - 1):
            self.pool.pop(listOfTasks[i], None)

    def optimizeSerialPool(self):
        taskChains = []
        for key, value in self.pool.items():
            list = []
            a = value.followingTasks
            if len(a) == 1 and value.type == 'sub':
                list.append(key)
                list = self.nextTask(a[0], list)
            if len(list) > 1:
                taskChains.append(list)
        sets = [set(l) for l in taskChains]
        tmp = [l for l, s in zip(taskChains, sets) if not any(s < other for other in sets)]
        taskChains = [item for item in taskChains if item in tmp]
        for item in taskChains:
            self.combineTasks(listOfTasks=item)

    def __eq__(self, other):
        if len(self.pool) != len(other.pool):
            return False
        shared_items = {k: self.pool[k] for k in self.pool if k in other.pool and self.pool[k] == other.pool[k]}
        if len(self.pool) == len(shared_items):
            return True
        else:
            return False


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
        self.cost = cost  # Costs
        self.color = "gray"  # Default color
        self.dep = self.findDependencies()  # Find dependencies based on op
        self.subtasks = self.findSubtasks(taskpool=taskpool)
        self.parent = None
        self.followingTasks = []

        tmp_split = re.split('_|\^', result.name)
        if len(tmp_split) <= 2:
            raise Exception('This should not happen')

        self.iteration = int(tmp_split[2])
        self.block = int(tmp_split[1])

        if len(tmp_split) == 3:
            self.type = 'main'
        else:
            self.type = 'sub'
            taskpool.unassignedSubtasks.append(result)

        self.resultString = self.getResultString()
        self.opType = self.typeOfOperation()
        self.color = taskpool.getColor(type=self.opType)

    def updateTask(self, op, cost, taskpool):
        self.op = op
        self.cost = cost
        self.dep = self.findDependencies()
        self.opType = self.typeOfOperation()
        self.color = taskpool.getColor(type=self.opType)

    def getResultString(self):
        tmp = self.translateSymbolString(self.result)
        if re.match(r"u_{\d+}\^{\d+}$", tmp):
            name = f'${tmp}$'
        else:
            name = f''
        return name

    def findSubtasks(self, taskpool):
        tmpRegex = self.translateSymbolString(self.result) + ("_{\d+}$")
        tmpRegex = tmpRegex.replace('^', '\^').replace('}', '\}').replace('{', '\{')
        tmp = [key for key in taskpool.unassignedSubtasks if
               re.compile(tmpRegex).match(self.translateSymbolString(key))]
        taskpool.unassignedSubtasks = [item for item in taskpool.unassignedSubtasks if item not in tmp]
        for item in tmp:
            taskpool.pool[item].parent = self.result
        return tmp

    def findDependencies(self):
        """
        Gets the dependencies from the operation (expects dependencies to start with u)

        :return: dependencies
        """
        tmp = [item for item in self.op.atoms() if (isinstance(item, sy.Symbol) and item.name.startswith('u'))]
        return tmp

    def typeOfOperation(self):
        if len(self.op.args) > 0:
            if isinstance(self.op.args[0], sy.Symbol):
                if len(re.split('u_|u\^', self.op.args[0].name)) > 1:
                    if self.op.is_Add:
                        type = '+'
                    else:
                        raise Exception('Does this exists?')
                else:
                    r1 = re.search(r"(\*u_\d+\^\d+(_\d+)*)", str(self.op))
                    replace = r1.group(1)
                    type = str(self.op).replace(replace, '').replace('**', '^').replace("(", "{").replace(")", "}")
                    # type = f"{self.op.args[0]}"
            elif isinstance(self.op.args[0], sy.Integer):
                if self.op.func.is_Mul:
                    func = '*'
                elif self.op.func.is_Add:
                    func = '+'
                else:
                    raise Exception(f'Unknown func in {self.result}={self.op} with {type(self.op.func)}')
                type = f'{self.op.args[0]}{func}'
            elif isinstance(self.op.args[0], sy.Pow):
                r1 = re.search(r"(\*u_\d+\^\d+(_\d+)*)", str(self.op))
                replace = r1.group(1)
                type = str(self.op).replace(replace, '').replace('**', '^').replace("(", "{").replace(")", "}")
                # type = f'{self.op.args[0].args[0]}^{{{self.op.args[0].args[1]}}}'
            else:
                raise Exception(f'Unknown operation in {self.result}={self.op} with {type(self.op.args[0])}')
        else:
            type = 'IC'

        return f'${type}$'

    def translateSymbolString(self, symbol):
        return re.compile(r'(\d+)').sub(r'{\1}', str(symbol))

    def __eq__(self, other):
        if (self.op == other.op and self.result == other.result and self.iteration == other.iteration and
                self.block == other.block and self.opType == other.opType):
            return True
        else:
            return False

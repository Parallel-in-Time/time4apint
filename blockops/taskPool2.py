import sympy as sy
import re

COLOR_LIST = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974',
              '#64b5cd', '#818d6d', '#7f0c17', '#c4ddb2', '#2ab414', '#f98131', '#08786d', '#142840',
              '#d065b5','#a73307']

class Counter(object):
    """Helping class to be used as a counter (value stored in n attribute)"""

    def __init__(self):
        self.n = 0

    def increment(self):
        """Increment counter value by one"""
        self.n += 1

    def __str__(self):
        return str(self.n)

class TasksPool(object):
    """Helping class to store the description of the tasks"""

    def __init__(self):
        self.counter = Counter()
        self.tasks = {}
        self.results = {}
        self.pool = {}
        self.colorLookup = {'$IC$': 'lightgrey'}
        self.colorCounter = 0
        self.save = []

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

    def getTask(self, name):
        return self.pool[name]

    def addTask(self, ope, inp, dep, n, k, blockIters, result=None):
        """
        Add a task to the pool, considering one operator, one input,
        and a task dependency.

        Parameters
        ----------
        ope : Symbol
            The operator used for this task.
        inp : Expression
            The input of this task (full expression).
        dep : sympy expression
            The dependencies for this task, in function of other tasks or
            block variables.

        Returns
        -------
        task : Symbol
            The symbol fo this task (T0, T1, ...).
        res : Expression
            The result of this task (full expression).
        """
        res = (ope * inp).simplify()
        if res in self.results:
            # Task already in pool
            task = self.results[res]
        elif -res in self.results:
            # Negative of the task already in pool
            task = -self.results[-res]
        else:
            # Task not in pool, create and add it
            if result is None:
                task = sy.symbols(f'u_{n}^{k}_{self.counter}', commutative=False)
            else:
                task = result
            # print(task, ':', ope, '--', inp)
            self.tasks[task] = (ope, inp, dep)
            if type(ope) == sy.Integer or type(ope) == sy.core.numbers.Zero:
                cost = 0
            elif str(ope) in blockIters:
                cost = blockIters[str(ope)].cost
            else:
                cost = 5
            self.pool[task] = Task(op=ope, fullOp = res, result=task, cost = cost, taskpool=self, n=n, k=k, dep=dep)
            self.results[res] = task
            self.counter.increment()

        return task, res

    def createTasks(self, dico, n, k, res, blockIters, depths = 0):
        """
        Function extracting the tasks from a factorized dictionnary

        Parameters
        ----------
        dico : dict
            Dictionnary containig a factorized expression

        Returns
        -------
        res : Expression
            Full expression for the result of the dictionnary.
        dep : Expression
            Expression for the result in function of tasks.
        """
        res_tmp = 0
        dep = 0
        for ope, inp in dico.items():
            if inp == 1:
                res_tmp = res_tmp + ope
                dep = res_tmp + ope
                self.save.append([res_tmp, dep])
            elif type(inp) is dict:
                r1, d1 = self.createTasks(dico=inp, n=n, k=k, res= None, blockIters=blockIters, depths=depths+1)
                t, r = self.addTask(ope=ope, inp=r1, dep=d1, n=n, k=k, blockIters=blockIters)
                if depths == 0:
                    self.save.append([t, r])
                res_tmp = res_tmp + r
                dep = dep + t
            elif type(inp) is sy.Symbol:
                t, r = self.addTask(ope=ope, inp=inp, dep = inp, n=n, k=k, blockIters=blockIters)
                res_tmp = res_tmp + r
                dep = dep + t
                if depths == 0:
                    self.save.append([t,r])
            else:
                raise ValueError('AAAAAAAAAAAAAAAAHHHHHH')

        if res is not None and depths==0:
            depe = self.save[0][0]
            fullOp = self.save[0][1]
            for i in range(1,len(self.save)):
                depe = depe + self.save[i][0]
                fullOp = fullOp + self.save[i][1]

            self.pool[res] = Task(op='+', fullOp = fullOp, result=res, cost = 0, taskpool=self, n=n, k=k, dep=depe)
        return res_tmp, dep

    def removeZeroTasks(self):
        remove_list = []
        for key, value in self.pool.items():
            if type(value.op) == sy.core.numbers.NegativeOne or type(value.op) == sy.core.numbers.One:
                for item in value.dep:
                    task = self.getTask(item)
                    task.followingTasks.remove(key)
                    for y in value.followingTasks:
                        task.followingTasks.append(y)
                for item in value.followingTasks:
                    task = self.getTask(item)
                    task.dep.remove(key)
                    for y in value.dep:
                        task.dep.append(y)
                remove_list.append(key)
        for item in remove_list:
            try:
                del self.pool[item]
            except KeyError:
                raise Exception('should not happen')

    def setCosts(self):
        for key, value in self.pool.items():
            if type(value.op) == sy.Pow:
                if "_C" in str(value.op):
                    value.cost = 2
                else:
                    value.cost = 8
            elif "T_" in str(value.op):
                value.cost = 0.0
            else:
                value.cost = 0

class Task(object):
    """Represents one task"""

    def __init__(self, op, result, cost, taskpool, dep, n, k, fullOp):
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
        self.color = "gray" # Default color
        self.fullOP = fullOp

        self.dep = []
        if type(dep) == sy.Add:
            for item in dep.args:
                if type(item) == sy.Mul:
                    if type(item.args[0]) == sy.core.numbers.NegativeOne:
                        self.dep.append(item.args[1])
                    elif type(item.args[0]) == sy.Integer:
                        self.dep.append(item.args[1])
                    else:
                        raise Exception('test')
                else:
                    self.dep.append(item)
        elif type(dep) == sy.Symbol:
            self.dep = [dep]
        elif dep is None:
            self.dep = []
        else:
            raise Exception('a')

        for item in self.dep:
            task = taskpool.getTask(item)
            task.followingTasks.append(result)

        self.parent = None
        self.followingTasks = []

        self.iteration = k
        self.block = n

        tmp_split = re.split('_|\^', result.name)
        if len(tmp_split) == 3:
            self.type = 'main'
        else:
            self.type = 'sub'

        self.opType = f'${str(op).replace("(-1)","{-1}").replace("**","^")}$'
        if self.opType.startswith("$-"):
            self.opType = "$" + self.opType[2:]
        self.color = taskpool.getColor(type=self.opType)
        #self.subtasks = self.findSubtasks(taskpool=taskpool)

        # if len(tmp_split) == 3:
        #     self.type = 'main'
        # else:
        #     self.type = 'sub'
        #     taskpool.unassignedSubtasks.append(result)

        # self.resultString = self.getResultString()
        # self.opType = self.typeOfOperation()
        # self.color = taskpool.getColor(type=self.opType)

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

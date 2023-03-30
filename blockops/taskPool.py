import sympy as sy
import re

from blockops.run import PintRun

COLOR_LIST = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974',
              '#64b5cd', '#818d6d', '#7f0c17', '#c4ddb2', '#2ab414', '#f98131', '#08786d', '#142840',
              '#d065b5', '#a73307']


class Counter(object):
    """Helping class to be used as a counter (value stored in n attribute)"""

    def __init__(self):
        self.n = 0

    def increment(self):
        """Increment counter value by one"""
        self.n += 1

    def __str__(self):
        return str(self.n)


class Task(object):
    """Represents one task"""

    def __init__(self, op: sy.Expr, result: sy.Expr, cost: float, dep: list, n: int, k: int, fullOp: sy.Expr) -> None:
        """
        Creates a task based.

        Parameters
        ----------
        op : sy.Expr
            DESCRIPTION. Represents the expression that the task performs.
        result : sy.Expr
            DESCRIPTION. A representation for the result of the expression
        cost : float
            The cost of this task
        dep : sy.Add, sy.Symbol, sy.Mul, None
            Expression representing the dependencies of this task
        n : int
            The block associated with this task
        k : int
            The iteration associated with this task
        fullOp : sy.Expr
            Full operation

        """
        self.op = op  # Operation (sympy expression)
        self.result = result  # Result (what is computed by this task)
        self.cost = cost  # Costs
        self.color = "gray"  # Default color
        self.fullOP = fullOp  # Full operation

        # Set dependencies
        self.dep = []
        if type(dep) == sy.Add:
            for item in dep.args:
                if type(item) == sy.Mul:
                    if type(item.args[0]) == sy.core.numbers.NegativeOne or type(item.args[0]) == sy.Integer:
                        self.dep.append(item.args[1])
                    else:
                        raise Exception(f'Unknwon first argument in task {type(item.args[0])}')
                else:
                    self.dep.append(item)
        elif type(dep) == sy.Symbol:
            self.dep = [dep]
        elif type(dep) == sy.Mul:
            for item in dep.args:
                if type(dep) == sy.Symbol:
                    self.dep.append(item)
        elif dep is None:
            self.dep = []
        else:
            raise Exception(f'Unknown type of dependency: {type(self.dep)}')

        # Helper to know about parent and following tasks
        self.parent = None
        self.followingTasks = []

        # Iteration and block
        self.iteration = k
        self.block = n

        # Type of operation (main == full block operation, sub == subtask for a block iteration)
        if len(re.split('_|\^', result.name)) == 3:
            self.type = 'main'
        else:
            self.type = 'sub'

        # Operation as string
        self.opType = f'${str(op).replace("(-1)", "{-1}").replace("**", "^")}$'
        if self.opType.startswith("$-"):
            self.opType = "$" + self.opType[2:]


class TaskPool(object):
    """Helping class to store the description of the tasks"""

    def __init__(self, run: PintRun) -> None:
        """
        Creates a task pool for a parallel-in-time run

        Parameters
        ----------
        run : PintRun
            The PinT run which should be split into tasks
        """
        self.counter = Counter()  # Helper to assign unique task numbers
        self.tasks = {}  # Additional helper, can probably be removed
        self.results = {}  # Helper to store result of each task
        self.pool = {}  # Actual task pool
        self.colorLookup = {
            '$IC$': 'lightgrey'}  # Lookup table to assign the same color to task with the same operation
        self.colorCounter = 0  # Helper to identify unused colors
        self.highestLevelStorage = []  # Helper to set dependencies on highest expression level
        self.blockIteration = run.blockIteration  # Block iteration
        self.facBlockRules = run.facBlockRules  # factorized block rules

        # Create tasks from factorized block rules
        for key, value in self.facBlockRules.items():
            self.taskGenerator(rule=value['rule'], res=value['result'], n=key[0], k=key[1])

        # Simplify taskpool by removing task representing identity
        self.removeTasksRepresentingOne()

    def taskGenerator(self, rule, res: sy.Symbol, n: int, k: int) -> None:
        """
        Generates tasks based on a given rule.

        Parameters
        ----------
        rule : sy.Symbol, sy.Mul, sy.Add
            The rule to compute the block iteration for n and k
        res : sy.Symbol
            The name of the result
        n : int
            Current block
        k : int
            Current iteration
        """

        # If rule is just a copy of another task
        if type(rule) == dict:
            self.createTasks(dico=rule, n=n, k=k, res=res)
        elif type(rule) == sy.core.numbers.Zero:
            self.addTask(ope=sy.core.numbers.Zero(), inp=sy.core.numbers.Zero(), dep=None, n=n, k=k, result=res)
        elif rule is None:
            pass
        else:
            raise Exception(f'Unknown type of rule in task generator: {type(rule)}')

    def getColor(self, op: str) -> str:
        """
        Returns color to represent same type of operations

        Parameters
        ----------
        op : str
            Type of operation

        Returns
        -------
        res : str
            Color associated with operation
        """
        if op in self.colorLookup:
            return self.colorLookup[op]
        else:
            color = 'gray'
            if self.colorCounter < len(COLOR_LIST):
                color = COLOR_LIST[self.colorCounter]
                self.colorLookup[op] = color
                self.colorCounter += 1
            self.colorLookup[op] = color
            return color

    def getTask(self, name: sy.Symbol) -> Task:
        """
        Getter for one task

        Parameters
        ----------
        name : sy.Symbol
            Identifier for task

        Returns
        -------
        res : Task
            The task object
        """
        return self.pool[name]

    def addTask(self, ope, inp, dep, n, k, result=None):
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
        n : int
            The block of the task
        k : int
            The iteration of the task
        result : None, sy.Symbol
            Result if the results is known prior, otherwise the result
            representation is created.

        Returns
        -------
        task : Symbol
            The symbol fo this task (T0, T1, ...).
        res : Expression
            The result of this task (full expression).
        """
        res = (ope * inp).simplify()
        if res in self.results and type(res) != sy.core.numbers.Zero:
            # Task already in pool
            task = self.results[res]
        elif -res in self.results and type(res) != sy.core.numbers.Zero:
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
            elif str(ope) in self.blockIteration.blockOps:
                cost = self.blockIteration.blockOps[str(ope)].cost
            else:
                cost = 5
            self.pool[task] = self.createTask(op=ope, fullOp=res, result=task, cost=cost, n=n, k=k, dep=dep)
            self.results[res] = task
            self.counter.increment()

        return task, res

    def createTask(self, op, fullOp, result: sy.Symbol, cost: float, n: int, k: int, dep: sy.Symbol):
        """
        Function extracting the tasks from a factorized dictionary and
        creates multiple tasks

        Parameters
        ----------
        op : sy.core.numbers.Zero, sy.Symbol, sy.Pow, str
            Operation of task
        fullOp : sy.Mul,
            Op * approx
        result : sy.Symbol
            Symbol representing result
        cost : float
            Cost of operation
        n : int
            The block
        k : int
            The iteration
        dep: sy.Symbol, None
            Dependency of this operation

        Returns
        -------
        newTask : Task,
            New created task
        """
        newTask = Task(op=op, fullOp=fullOp, result=result, cost=cost, n=n, k=k, dep=dep)
        newTask.color = self.getColor(op=newTask.opType)
        for item in newTask.dep:
            task = self.getTask(item)
            task.followingTasks.append(newTask.result)
        return newTask

    def createTasks(self, dico: dict, n: int, k: int, res: sy.Symbol):
        """
        Function extracting the tasks from a factorized dictionary and
        creates multiple tasks

        Parameters
        ----------
        dico : dict
            Dictionary containing a factorized expression
        n : int
            The block
        k : int
            The iteration
        res: sy.Symbol. None
            Result

        Returns
        -------
        res : sy.Expr
            Full expression for the result of the dictionary.
        dep : sy.Expr
            Expression for the result in function of tasks.
        """

        res_tmp = 0
        dep = 0
        for ope, inp in dico.items():
            if inp == 1:
                res_tmp = res_tmp + ope
                dep = res_tmp + ope
                if res is not None:
                    self.highestLevelStorage.append([res_tmp, dep])
            elif type(inp) is dict:
                r1, d1 = self.createTasks(dico=inp, n=n, k=k, res=None)
                t, r = self.addTask(ope=ope, inp=r1, dep=d1, n=n, k=k)
                if res is not None:
                    self.highestLevelStorage.append([t, r])
                res_tmp = res_tmp + r
                dep = dep + t
            elif type(inp) is sy.Symbol:
                t, r = self.addTask(ope=ope, inp=inp, dep=inp, n=n, k=k)
                res_tmp = res_tmp + r
                dep = dep + t
                if res is not None:
                    self.highestLevelStorage.append([t, r])
            else:
                raise ValueError(f'CreateTask unknown type: {type(inp)}')

        if res is not None:
            depe = self.highestLevelStorage[0][0]
            fullOp = self.highestLevelStorage[0][1]
            for i in range(1, len(self.highestLevelStorage)):
                depe = depe + self.highestLevelStorage[i][0]
                fullOp = fullOp + self.highestLevelStorage[i][1]
            self.highestLevelStorage = []

            self.pool[res] = self.createTask(op='+', fullOp=fullOp, result=res, cost=0, n=n, k=k, dep=depe)
        return res_tmp, dep

    def removeTasksRepresentingOne(self) -> None:
        """
        Removes tasks from the pool that represent multiplication by the identity matrix
        """
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
                raise Exception(f'Failed to remove task {str(item.op)} from taskpool')

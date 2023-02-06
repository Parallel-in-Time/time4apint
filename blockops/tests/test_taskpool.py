import pytest
import sympy as sy

from ..taskpool import TaskPool, Task, COLOR_LIST


class TestTaskPool:

    def testConstructor(self):
        taskpool = TaskPool()
        assert {} == taskpool.pool
        assert {'$IC$': 'lightgrey'} == taskpool.colorLookup
        assert 0 == taskpool.colorCounter

    def testAddTask(self):
        u00 = sy.symbols(f'u_{0}^{0}', commutative=False)
        u10 = sy.symbols(f'u_{1}^{0}', commutative=False)
        zero = 0 * sy.symbols('null', commutative=False)
        G = sy.symbols(f'G', commutative=False)

        taskpool = TaskPool()
        taskpool.addTask(operation=zero, result=u00, cost=5)

        assert len(taskpool.pool) == 1

        taskpool = TaskPool()
        taskpool.addTask(operation=zero, result=u00, cost=5)
        taskpool.addTask(operation=G * u00, result=u10, cost=5)
        assert len(taskpool.pool) == 2
        assert taskpool.pool[u10].color == COLOR_LIST[0]
        assert taskpool.pool[u00].followingTasks == [u10]

    def testGetTask(self):
        u00 = sy.symbols(f'u_{0}^{0}', commutative=False)
        u10 = sy.symbols(f'u_{1}^{0}', commutative=False)
        zero = 0 * sy.symbols('null', commutative=False)
        G = sy.symbols(f'G', commutative=False)

        taskpool = TaskPool()
        taskpool.addTask(operation=zero, result=u00, cost=5)
        taskpool.addTask(operation=G * u00, result=u10, cost=5)

        task = Task(op=G * u00, result=u10, cost=5, taskpool=taskpool)

        task2 = taskpool.getTask(name=u10)

        assert task.followingTasks == task2.followingTasks
        assert task.op == task2.op
        assert task.cost == task2.cost
        assert task.dep == task2.dep
        assert task.subtasks == task2.subtasks
        assert task.iteration == task2.iteration
        assert task.block == task2.block
        assert task.type == task2.type
        assert task.resultString == task2.resultString
        assert task.opType == task2.opType

    def testEquals(self):
        u00 = sy.symbols(f'u_{0}^{0}', commutative=False)
        u10 = sy.symbols(f'u_{1}^{0}', commutative=False)
        u20 = sy.symbols(f'u_{2}^{0}', commutative=False)
        zero = 0 * sy.symbols('null', commutative=False)
        G = sy.symbols(f'G', commutative=False)
        F = sy.symbols(f'F', commutative=False)

        taskpool1 = TaskPool()
        taskpool1.addTask(operation=zero, result=u00, cost=5)
        taskpool1.addTask(operation=G * u00, result=u10, cost=5)

        taskpool2 = TaskPool()
        taskpool2.addTask(operation=zero, result=u00, cost=5)

        assert not taskpool1 == taskpool2

        taskpool2.addTask(operation=G * u00, result=u10, cost=5)

        assert taskpool1 == taskpool2

        taskpool1.addTask(operation=G * u10, result=u20, cost=5)
        taskpool2.addTask(operation=F * u10, result=u20, cost=5)

        assert not taskpool1 == taskpool2


class TestTask:

    def testConstructor(self):
        u00 = sy.symbols(f'u_{0}^{0}', commutative=False)
        u10 = sy.symbols(f'u_{1}^{0}', commutative=False)

        F = sy.symbols(f'F', commutative=False)
        G = sy.symbols(f'G', commutative=False)

        taskpool = TaskPool()
        task = Task(op=G * u00, result=u10, cost=5, taskpool=taskpool)

        assert task.block == 1
        assert task.cost == 5
        assert task.dep == [u00]
        assert task.type == 'main'
        assert task.resultString == '$u_{1}^{0}$'
        assert task.opType == '$G$'

    def testGetResultsString(self):
        u00 = sy.symbols('u_0^0', commutative=False)
        u10 = sy.symbols('u_1^0', commutative=False)
        u101 = sy.symbols('u_1^0_1', commutative=False)

        F = sy.symbols(f'F', commutative=False)
        G = sy.symbols(f'G', commutative=False)

        taskpool = TaskPool()
        task = Task(op=G * u00, result=u10, cost=5, taskpool=taskpool)

        task.result = u10
        tmp = task.getResultString()
        assert '$u_{1}^{0}$' == tmp

        task.result = u101
        tmp = task.getResultString()
        assert '$\\overline{u}_{1}^{0}$' == tmp

    def testFindSubstaks(self):
        u00 = sy.symbols('u_0^0', commutative=False)
        u10 = sy.symbols('u_1^0', commutative=False)
        zero = 0 * sy.symbols('null', commutative=False)
        u101 = sy.symbols('u_1^0_1', commutative=False)
        u102 = sy.symbols('u_1^0_2', commutative=False)

        F = sy.symbols(f'F', commutative=False)
        G = sy.symbols(f'G', commutative=False)

        taskpool = TaskPool()
        taskpool.addTask(operation=zero, result=u00, cost=5)
        taskpool.addTask(operation=G * u00, result=u10, cost=5)
        taskpool.addTask(operation=G * u00, result=u101, cost=5)
        taskpool.addTask(operation=G * u00, result=u102, cost=5)

        task = Task(op=u00 + u10, result=u10, cost=5, taskpool=taskpool)

        tmp = task.findSubtasks(taskpool=taskpool)
        assert [u101, u102] == tmp

    def testFindDependencies(self):
        u00 = sy.symbols('u_0^0', commutative=False)
        u10 = sy.symbols('u_1^0', commutative=False)
        task = Task(op=u00 + u10, result=u10, cost=5, taskpool=TaskPool())

        tmp = task.findDependencies()
        res = [u00, u10]
        for item in tmp:
            if item not in res:
                assert False
        assert len(res) == len(tmp)

    def testTypeOfOperation(self):
        u00 = sy.symbols('u_0^0', commutative=False)
        u10 = sy.symbols('u_1^0', commutative=False)
        G = sy.symbols('G', commutative=False)
        zero = 0 * sy.symbols('zero', commutative=False)

        task = Task(op=2 * u10, result=u10, cost=5, taskpool=TaskPool())
        tmp = task.typeOfOperation()
        assert '$2*$' == tmp

        task = Task(op=G * u10, result=u10, cost=5, taskpool=TaskPool())
        tmp = task.typeOfOperation()
        assert '$G$' == tmp

        task = Task(op=zero, result=u10, cost=5, taskpool=TaskPool())
        tmp = task.typeOfOperation()
        assert '$IC$' == tmp

        task = Task(op=u10 + u00, result=u10, cost=5, taskpool=TaskPool())
        tmp = task.typeOfOperation()
        assert '$+$' == tmp

    def testTranslateSymbolString(self):
        u10 = sy.symbols('u_10^0', commutative=False)
        task = Task(op=2 * u10, result=u10, cost=5, taskpool=TaskPool())
        tmp = task.translateSymbolString(u10)
        assert 'u_{10}^{0}' == tmp

        u10 = sy.symbols('u_10^10', commutative=False)
        task = Task(op=2 * u10, result=u10, cost=5, taskpool=TaskPool())
        tmp = task.translateSymbolString(u10)
        assert 'u_{10}^{10}' == tmp

    def testEqual(self):
        u10 = sy.symbols('u_1^0', commutative=False)
        u00 = sy.symbols('u_0^0', commutative=False)
        task = Task(op=u00 + u10, result=u10, cost=5, taskpool=TaskPool())

        task2 = Task(op=2 * u10, result=u10, cost=5, taskpool=TaskPool())

        assert not task == task2

        task2 = Task(op=u00 + u10, result=u10, cost=5, taskpool=TaskPool())

        assert task == task2

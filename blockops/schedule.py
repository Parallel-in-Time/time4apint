# Python import

import matplotlib.pyplot as plt
import numpy as np
from .taskpool import TaskPool
from matplotlib.patches import Rectangle

SCHEDULE_TYPES = {
    'BLOCK-BY-BLOCK': lambda taskPool, nProc, nPoints: PinTBlockByBlock(taskPool=taskPool, nProc=nProc,
                                                                        nPoints=nPoints),
    'WINDOWING': lambda taskPool, nProc, nPoints: PinTWindowing(taskPool=taskPool, nProc=nProc, nPoints=nPoints),
    'OPTIMAL': lambda taskPool, nProc, nPoints: Optimal(taskPool=taskPool, nProc=nProc, nPoints=nPoints)}


def getSchedule(taskPool: TaskPool, nProc: int, nPoints: int, schedule_type: str):
    if schedule_type not in SCHEDULE_TYPES:
        raise Exception(f"Schedule {type} not implemented, must be in {list(SCHEDULE_TYPES.keys())}")
    else:
        schedule = SCHEDULE_TYPES[schedule_type](taskPool=taskPool, nProc=nProc, nPoints=nPoints)
        schedule.computeSchedule()
        return schedule


class ScheduledTask():

    def __init__(self, proc, start, end, name, color='gray'):
        self.proc = proc
        self.start = start
        self.name = name
        self.end = end
        self.color = color


class Schedule:

    def __init__(self, taskPool, nProc, nPoints):
        self.schedule = {}
        self.schedule_name = ''
        self.taskPool = taskPool
        self.makespan = 0
        self.nProc = nProc
        self.startPointProc = np.zeros(self.nProc)
        self.nPoints = nPoints

    def computeSchedule(self):
        pass

    def getRuntime(self):
        return self.makespan

    def plot(self, figName, figSize=(8, 4.8)):
        fig, ax = plt.subplots(1, 1, figsize=figSize, num=figName)
        for key, value in self.schedule.items():
            time = value.end - value.start
            if time > 0:
                operation = value.name
                rec = Rectangle((value.start, value.proc + .225), time, .5, color='k', fc=value.color)
                ax.add_patch(rec)
                rx, ry = rec.get_xy()
                cx = rx + rec.get_width() / 2.0
                cy = ry + rec.get_height() / 2.0
                ax.annotate(operation, (cx, cy), color='w', weight='bold',
                            fontsize=6, ha='center', va='center')
        ax.set_xlim(0, self.makespan)
        ax.set_ylim(0, self.nProc)
        ax.set_yticks(np.linspace(self.nProc - 1, 0, self.nProc) + 0.5)
        ax.set_yticklabels(['P' + str(i) for i in range(self.nProc - 1, -1, -1)])
        plt.show()


class PinTBlockByBlock(Schedule):
    """
    Computes standard schedule based on block-by-block basis
    """

    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)
        self.distribution = np.array([int(self.nPoints / self.nProc + 1)] * (self.nPoints % self.nProc) +
                                     [int(self.nPoints / self.nProc)] * (self.nProc - self.nPoints % self.nProc))
        self.point_to_proc = {}
        start = 0
        for i in range(self.nProc):
            for j in range(start, start + self.distribution[i]):
                self.point_to_proc[j] = i
            start += self.distribution[i]
        self.availableTasks = [key for key, value in self.taskPool.pool.items() if len(value.dep) == 0]
        self.notAvailableTasks = [key for key, value in self.taskPool.pool.items() if len(value.dep) > 0]
        self.finishedTasks = []
        self.schedule_name = '"PinT Block-by-Block"'

    def pickTask(self):
        taskName = self.availableTasks[0]
        task = self.taskPool.getTask(name=taskName)
        tmpIt = task.iteration
        tmpB = task.block
        for item in self.availableTasks:
            tmp = self.taskPool.getTask(name=item)
            if tmp.iteration < tmpIt:
                taskName = item
                task = tmp
                tmpIt = task.iteration
                tmpB = task.block
            elif tmp.iteration == tmpIt:
                if tmp.block > tmpB:
                    taskName = item
                    task = tmp
                    tmpIt = task.iteration
                    tmpB = task.block
            else:
                continue
        return taskName

    def assignTask(self, taskName):
        task = self.taskPool.getTask(taskName)
        possibleStartTime = self.startPointProc[self.point_to_proc[task.block]]
        tmp_commu = 0
        for depTask in task.dep:
            if self.schedule[depTask].end + tmp_commu > possibleStartTime:
                possibleStartTime = self.schedule[depTask].end + tmp_commu

        self.schedule[taskName] = ScheduledTask(proc=self.point_to_proc[task.block],
                                                start=possibleStartTime,
                                                end=possibleStartTime + task.cost,
                                                name=task.name,
                                                color=task.color)

        self.startPointProc[self.point_to_proc[task.block]] = self.schedule[taskName].end
        if self.schedule[taskName].end > self.makespan:
            self.makespan = self.schedule[taskName].end

    def updateLists(self, taskName):
        # Remove task from available task and add to finished
        self.finishedTasks += [taskName]
        self.availableTasks = [item for item in self.availableTasks if item != taskName]
        # Iterating on all following tasks
        task = self.taskPool.getTask(name=taskName)
        for item in task.followingTasks:
            folTask = self.taskPool.getTask(name=item)
            # Check if all dependencies are finished
            if sum(el in self.finishedTasks for el in folTask.dep) == len(folTask.dep):
                # Check if task is not already finished or available
                if item not in self.finishedTasks and item not in self.availableTasks:
                    # Add task to available tasks and remove from non available
                    self.availableTasks.append(item)
                    self.notAvailableTasks = [tmp for tmp in self.notAvailableTasks if tmp != item]

    def computeSchedule(self):
        while len(self.availableTasks) != 0:
            taskName = self.pickTask()
            self.assignTask(taskName=taskName)
            self.updateLists(taskName=taskName)


class PinTWindowing(Schedule):

    def __init__(self, *args: object, **kwargs: object):
        raise Exception('not implemented')
        super().__init__(*args, **kwargs)
        self.schedule_name = '"PinTWindowing"'


class Optimal(Schedule):
    """
    Calculates an optimal schedule using a simple greedy approach.
    Assumes unlimited processes and does not minimize the number of processes.
    """

    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)
        self.availableTasks = [key for key, value in self.taskPool.pool.items() if len(value.dep) == 0]
        self.notAvailableTasks = [key for key, value in self.taskPool.pool.items() if len(value.dep) > 0]
        self.finishedTasks = []
        self.schedule_name = '"Optimal"'
        self.startPointProc = np.zeros(20000)

    def pickTask(self):
        # Choose the cheapest task (Typically corresponds to coarse solves that often allow new tasks)
        # Random choices are possible
        return self.availableTasks[np.argmin([self.taskPool.getTask(item).cost for item in self.availableTasks])]

    def assignTask(self, taskName):
        task = self.taskPool.getTask(taskName)
        minimal_start_time = 0
        for depTask in task.dep:
            if self.schedule[depTask].end > minimal_start_time:
                minimal_start_time = self.schedule[depTask].end
        # Get the first process who is free for the minimal start time
        proc = next(x[0] for x in enumerate(self.startPointProc) if x[1] <= minimal_start_time)
        self.schedule[taskName] = ScheduledTask(proc=proc,
                                                start=minimal_start_time,
                                                end=minimal_start_time + task.cost,
                                                name=task.opType,
                                                color=task.color)
        self.startPointProc[proc] = self.schedule[taskName].end
        if self.schedule[taskName].end > self.makespan:
            self.makespan = self.schedule[taskName].end

    def updateLists(self, taskName):
        self.finishedTasks += [taskName]
        self.availableTasks = [item for item in self.availableTasks if item != taskName]
        # Iterating on all following tasks
        task = self.taskPool.getTask(name=taskName)
        for item in task.followingTasks:
            folTask = self.taskPool.getTask(name=item)
            # Check if all dependencies are finished
            if sum(el in self.finishedTasks for el in folTask.dep) == len(folTask.dep):
                # Check if task is not already finished or available
                if item not in self.finishedTasks and item not in self.availableTasks:
                    # Add task to available tasks and remove from non available
                    self.availableTasks.append(item)
                    self.notAvailableTasks = [tmp for tmp in self.notAvailableTasks if tmp != item]

    def computeSchedule(self):
        while len(self.availableTasks) != 0:
            taskName = self.pickTask()
            self.assignTask(taskName=taskName)
            self.updateLists(taskName=taskName)
        self.nProc = len(np.where(self.startPointProc != 0)[0])

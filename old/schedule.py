# Python import
import matplotlib.pyplot as plt
import numpy as np
from .taskPool import TaskPool
from matplotlib.patches import Rectangle
from typing import Dict
from matplotlib.lines import Line2D


class ScheduledTask():

    def __init__(self, proc, start, end, name, color='gray'):
        self.proc = proc
        self.start = start
        self.name = name
        self.end = end
        self.color = color


class Schedule:
    NAME = None  # unique name for the schedule
    IDS = set()  # list of ids that can be used for usage of this schedule

    def __init__(self, taskPool, nProc, nPoints):
        self.schedule = {}
        self.taskPool = taskPool
        self.makespan = 0
        self.nProc = nProc
        self.startPointProc = np.zeros(self.nProc)
        self.nPoints = nPoints

    def computeSchedule(self):
        raise NotImplementedError(
            'abstract method, should be implemented in children class')

    @staticmethod
    def getDefaultNProc(N):
        """Return a default number of processors for a given number of block"""
        return None

    def getRuntime(self):
        return self.makespan

    def plot(self, figName: str, figSize: tuple = (8, 4.8), saveFig: str = ""):
        fig, ax = plt.subplots(1, 1, figsize=figSize, num=figName)
        colors = {}
        for key, value in self.schedule.items():
            time = value.end - value.start
            if time > 0:
                operation = value.name
                rec = Rectangle((value.start, value.proc + .225), time, .5, color='k', fc=value.color)
                ax.add_patch(rec)
                rx, ry = rec.get_xy()
                cx = rx + rec.get_width() / 2.0
                cy = ry + rec.get_height() / 2.0
                if value.color not in colors:
                    colors[value.color] = operation
                # ax.annotate(operation, (cx, cy), color='w', weight='bold',
                #             fontsize=6, ha='center', va='center')
        ax.set_xlim(0, self.makespan)
        ax.set_ylim(0, self.nProc)
        ax.set_yticks(np.linspace(self.nProc - 1, 0, self.nProc) + 0.5)
        ax.set_yticklabels(['P' + str(i) for i in range(self.nProc - 1, -1, -1)])
        ax.set_ylabel(ylabel='Processor rank')
        ax.set_xlabel(xlabel='Computation cost')
        leg = [Line2D([0], [0], marker='o', color='w', label=value,
                      markerfacecolor=key, markersize=15) for key, value in colors.items()]
        plt.legend(handles=leg, title='Task description', loc='upper center', bbox_to_anchor=(0.5, 1.25),
                   ncol=5, fancybox=True, shadow=True, numpoints=1,
                   fontsize=16)
        if saveFig != "":
            fig.savefig(saveFig, bbox_inches='tight', pad_inches=0.5)
        plt.show()


# -----------------------------------------------------------------------------
# Inherited specialized class
# -----------------------------------------------------------------------------
SCHEDULE_TYPES: Dict[str, Schedule] = {}


def register(cls: Schedule) -> Schedule:
    for stringID in cls.IDS:
        SCHEDULE_TYPES[stringID] = cls
    return cls


@register
class PinTBlockByBlock(Schedule):
    """
    Computes standard schedule based on block-by-block basis
    """

    NAME = "PinT Block-by-Block"
    IDS = {'BLOCK-BY-BLOCK', 'BbB'}

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
        self.availableTasks = set([key for key, value in self.taskPool.pool.items() if len(value.dep) == 0])
        self.notAvailableTasks = set([key for key, value in self.taskPool.pool.items() if len(value.dep) > 0])
        self.finishedTasks = set([])

    def pickTask(self):
        taskName = next(iter(self.availableTasks))
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
                                                name=task.opType,
                                                color=task.color)

        self.startPointProc[self.point_to_proc[task.block]] = self.schedule[taskName].end
        if self.schedule[taskName].end > self.makespan:
            self.makespan = self.schedule[taskName].end

    def updateLists(self, taskName):
        # Remove task from available task and add to finished
        self.finishedTasks.add(taskName)
        self.availableTasks.remove(taskName)
        # Iterating on all following tasks
        task = self.taskPool.getTask(name=taskName)
        for item in task.followingTasks:
            folTask = self.taskPool.getTask(name=item)
            # Check if all dependencies are finished
            if sum(el in self.finishedTasks for el in folTask.dep) == len(folTask.dep):
                # Check if task is not already finished or available
                if item not in self.finishedTasks and item not in self.availableTasks:
                    # Add task to available tasks and remove from non available
                    self.availableTasks.add(item)
                    self.notAvailableTasks.remove(item)

    def computeSchedule(self):
        while len(self.availableTasks) != 0:
            taskName = self.pickTask()
            self.assignTask(taskName=taskName)
            self.updateLists(taskName=taskName)

    @staticmethod
    def getDefaultNProc(N):
        return N


@register
class PinTWindowing(Schedule):
    NAME = "PinTWindowing"
    IDS = {'WINDOWING'}

    def __init__(self, *args: object, **kwargs: object):
        raise NotImplementedError()
        super().__init__(*args, **kwargs)


@register
class LowestCostFirst(Schedule):
    """
    Calculates an schedule using a list approach where the task with lowest cost is schedules first. This assumes
    that the cheapest tasks corresponds to lower lever tasks which helps most to enable new computations.
    """
    NAME = "LowestCostFirst"
    IDS = {"LOWEST-COST-FIRST", "LCF", "LowestCostFirst"}

    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)
        self.availableTasks = set([key for key, value in self.taskPool.pool.items() if len(value.dep) == 0])
        self.notAvailableTasks = set([key for key, value in self.taskPool.pool.items() if len(value.dep) > 0])
        self.finishedTasks = set([])

    def pickTask(self):
        tmp = [[self.taskPool.getTask(item).cost,
                self.taskPool.getTask(item).iteration,
                self.taskPool.getTask(item).block, item] for item in self.availableTasks]
        return min(tmp, key=lambda x: (x[0], x[1], x[2]))[3]

    def assignTask(self, taskName):
        task = self.taskPool.getTask(taskName)
        minimal_start_time = 0
        for depTask in task.dep:
            if self.schedule[depTask].end > minimal_start_time:
                minimal_start_time = self.schedule[depTask].end
        # Get the first process who is free for the minimal start time
        tmp = np.where(self.startPointProc <= minimal_start_time)[0]
        if len(tmp) > 0:
            proc = tmp[0]
        else:
            proc = np.argmin(self.startPointProc)
            minimal_start_time = self.startPointProc[proc]
        self.schedule[taskName] = ScheduledTask(proc=proc,
                                                start=minimal_start_time,
                                                end=minimal_start_time + task.cost,
                                                name=task.opType,
                                                color=task.color)
        self.startPointProc[proc] = self.schedule[taskName].end
        if self.schedule[taskName].end > self.makespan:
            self.makespan = self.schedule[taskName].end

    def updateLists(self, taskName):
        self.finishedTasks.add(taskName)
        self.availableTasks.remove(taskName)
        # Iterating on all following tasks
        task = self.taskPool.getTask(name=taskName)
        for item in task.followingTasks:
            folTask = self.taskPool.getTask(name=item)
            # Check if all dependencies are finished
            if sum(el in self.finishedTasks for el in folTask.dep) == len(folTask.dep):
                # Check if task is not already finished or available
                if item not in self.finishedTasks and item not in self.availableTasks:
                    # Add task to available tasks and remove from non available
                    self.availableTasks.add(item)
                    self.notAvailableTasks.remove(item)

    def computeSchedule(self):
        while len(self.availableTasks) != 0:
            taskName = self.pickTask()
            self.assignTask(taskName=taskName)
            self.updateLists(taskName=taskName)
        self.nProc = len(np.where(self.startPointProc != 0)[0])


@register
class Optimal(Schedule):
    """
    Calculates an optimal schedule using a simple greedy approach.
    Assumes unlimited processes and does not minimize the number of processes.
    """
    NAME = "Optimal"
    IDS = {"OPTIMAL", "OPT"}

    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)
        self.availableTasks = set([key for key, value in self.taskPool.pool.items() if len(value.dep) == 0])
        self.notAvailableTasks = set([key for key, value in self.taskPool.pool.items() if len(value.dep) > 0])
        self.finishedTasks = set([])
        self.startPointProc = np.zeros(20000)

    def pickTask(self):
        # Choose the cheapest task (Typically corresponds to coarse solves that often allow new tasks)
        # Random choices are possible
        tmp = [[self.taskPool.getTask(item).cost, item] for item in self.availableTasks]
        return min(tmp, key=lambda x: x[0])[1]

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
        self.finishedTasks.add(taskName)
        self.availableTasks.remove(taskName)
        # Iterating on all following tasks
        task = self.taskPool.getTask(name=taskName)
        for item in task.followingTasks:
            folTask = self.taskPool.getTask(name=item)
            # Check if all dependencies are finished
            if sum(el in self.finishedTasks for el in folTask.dep) == len(folTask.dep):
                # Check if task is not already finished or available
                if item not in self.finishedTasks and item not in self.availableTasks:
                    # Add task to available tasks and remove from non available
                    self.availableTasks.add(item)
                    self.notAvailableTasks.remove(item)

    def computeSchedule(self):
        while len(self.availableTasks) != 0:
            taskName = self.pickTask()
            self.assignTask(taskName=taskName)
            self.updateLists(taskName=taskName)
        self.nProc = len(np.where(self.startPointProc != 0)[0])


def getSchedule(taskPool: TaskPool, nProc: int, nPoints: int, scheduleType: str
                ) -> Schedule:
    if scheduleType not in SCHEDULE_TYPES:
        raise Exception(f"Schedule {type} not implemented, must be in {list(SCHEDULE_TYPES.keys())}")
    else:
        ScheduleClass = SCHEDULE_TYPES[scheduleType]
        nProc = ScheduleClass.getDefaultNProc(nPoints - 1) if nProc is None else nProc
        schedule = ScheduleClass(taskPool=taskPool, nProc=nProc, nPoints=nPoints)
        schedule.computeSchedule()
        return schedule

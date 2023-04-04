import numpy as np
import sympy as sy

from blockops.scheduler import register, ScheduledTask, TaskPool
from blockops.scheduler.listScheduler import listScheduler
from blockops.utils.params import setParams


@register
@setParams(
)
class PinTBlockByBlock(listScheduler):
    """
    Computes standard parallel-in-time schedule based on block-by-block basis
    """

    NAME = "PinT Block-by-Block"
    IDS = {'BLOCK-BY-BLOCK', 'BbB'}

    def __init__(self, taskPool: TaskPool, nProc: int, nPoints: int) -> None:
        """
        Constructor for PinTBlockByBlock scheduler
        """
        super().__init__(taskPool=taskPool, nProc=nProc, nPoints=nPoints)

        # Compute which time points are located on which process
        self.distribution = np.array([int(self.nPoints / self.nProc + 1)] * (self.nPoints % self.nProc) +
                                     [int(self.nPoints / self.nProc)] * (self.nProc - self.nPoints % self.nProc))
        self.pointToProc = {}
        start = 0
        for i in range(self.nProc):
            for j in range(start, start + self.distribution[i]):
                self.pointToProc[j] = i
            start += self.distribution[i]

    def pickTask(self) -> sy.Symbol:
        """
        Contains logic to pick the next task to schedule.

        Selects tasks based on the following priotirization:
            - Earliest iteration first
            - Latest time first

        Returns
        -------
        taskName : sy.Symbol
            Name of the task to be scheduled next
        """

        # Pick the first task
        taskName = next(iter(self.availableTasks))
        task = self.taskPool.getTask(name=taskName)
        tmpIt = task.iteration
        tmpB = task.block

        # Iterates over all tasks and checks if another task has higher priority
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

    def assignTask(self, taskName: sy.Symbol) -> None:
        """
        Computes the earliest starting point for the task *taskName*.
        The starting point depends on the prerequisite tasks of *taskName*
        and the process associated with the task

        Parameters
        ----------
        taskName : sy.Symbol
            The name of the task to be scheduled
        """

        # Get task object
        task = self.taskPool.getTask(taskName)

        # Compute earliest start point
        possibleStartTime = self.startPointProc[self.pointToProc[task.block]]
        tmp_commu = 0
        for depTask in task.dep:
            if self.schedule[depTask].end + tmp_commu > possibleStartTime:
                possibleStartTime = self.schedule[depTask].end + tmp_commu

        self.schedule[taskName] = ScheduledTask(proc=self.pointToProc[task.block],
                                                start=possibleStartTime,
                                                end=possibleStartTime + task.cost,
                                                name=task.opType,
                                                color=task.color)

        self.startPointProc[self.pointToProc[task.block]] = self.schedule[taskName].end

        # Update makespan if required
        if self.schedule[taskName].end > self.makespan:
            self.makespan = self.schedule[taskName].end

    @staticmethod
    def getDefaultNProc(N: int) -> int:
        """
        Returns the standard choice of processes for this scheduler
        based on the number of blocks

        Parameters
        ----------
        N : int
            TODO

        Returns
        -------
        N : int
            TODO
        """
        return N

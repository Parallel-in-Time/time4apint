import numpy as np
import sympy as sy

from blockops.scheduler import register, ScheduledTask, TaskPool
from blockops.scheduler.listScheduler import listScheduler
from blockops.utils.params import setParams


@register
@setParams(
)
class LowestCostFirst(listScheduler):
    """
    Calculates a schedule using a list approach where the task with the
    lowest cost is schedules first. This assumes that the cheapest tasks
    corresponds to lower lever tasks which helps most to enable new
    computations.
    """
    NAME = "LowestCostFirst"
    IDS = {"LOWEST-COST-FIRST", "LCF"}

    def __init__(self, taskPool: TaskPool, nProc: int, nPoints: int) -> None:
        """
        Constructor for LowestCostFirst scheduler
        """
        super().__init__(taskPool=taskPool, nProc=nProc, nPoints=nPoints)

    def pickTask(self) -> sy.Symbol:
        """
        Contains logic to pick the next task to schedule.

        Selects tasks based on the following priotirization:
            - Task with lowest costs

        Returns
        -------
        taskName : sy.Symbol
            Name of the task to be scheduled next
        """
        tmp = [[self.taskPool.getTask(item).cost,
                self.taskPool.getTask(item).iteration,
                self.taskPool.getTask(item).block, item] for item in self.availableTasks]
        return min(tmp, key=lambda x: (x[0], x[1], x[2]))[3]

    def assignTask(self, taskName: sy.Symbol) -> None:
        """
        Computes the earliest starting point for the task *taskName*.
        The starting point depends on the prerequisite tasks of *taskName*.

        Parameters
        ----------
        taskName : sy.Symbol
            The name of the task to be scheduled
        """
        # Get task
        task = self.taskPool.getTask(taskName)

        # Compute the minimum start time based on the prerequisites
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

        # Update minimum runtime if required
        if self.schedule[taskName].end > self.makespan:
            self.makespan = self.schedule[taskName].end

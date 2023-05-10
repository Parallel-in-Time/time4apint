import numpy as np
import sympy as sy

from blockops.scheduler import register, ScheduledTask, TaskPool
from blockops.scheduler.listScheduler import listScheduler
from blockops.utils.params import setParams


@register
@setParams(
)
class Optimal(listScheduler):
    """
    Calculates an optimal schedule using a simple greedy approach.
    Assumes unlimited processes and does not minimize the number of processes.
    """
    NAME = "Optimal"
    IDS = {"OPTIMAL", "OPT"}

    def __init__(self, taskPool: TaskPool, nProc: int, nPoints: int) -> None:
        """
        Constructor for optimal scheduler
        """
        super().__init__(taskPool=taskPool, nProc=nProc, nPoints=nPoints)
        self.startPointProc = np.zeros(20000)

    def pickTask(self) -> sy.Symbol:
        """
        Contains logic to pick the next task to schedule

        Choose the cheapest task (Typically corresponds to
        coarse solves that often allow new tasks)
        Random choices are possible

        Returns
        -------
        taskName : sy.Symbol
            Name of the task to be scheduled next
        """
        tmp = [[self.taskPool.getTask(item).cost, item] for item in self.availableTasks]
        return min(tmp, key=lambda x: x[0])[1]

    def assignTask(self, taskName):
        """
        Computes the earliest starting point for the task *taskName*.
        Assigns the task to process as soon as possible
        """
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

    def computeSchedule(self):
        """
        Main routine to compute a schedule.
        Calls the parent function and updates the number of processes used
        """
        super(Optimal, self).computeSchedule()
        self.nProc = len(np.where(self.startPointProc != 0)[0])

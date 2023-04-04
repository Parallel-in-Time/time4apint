import sympy as sy
from abc import ABC, abstractmethod

from blockops.scheduler import Scheduler, TaskPool
from blockops.utils.params import setParams

@setParams(
)
class listScheduler(Scheduler, ABC):
    """
    Abstract list scheduler class
    """

    NAME = ""
    IDS = {}

    def __init__(self, taskPool: TaskPool, nProc: int, nPoints: int) -> None:
        """
        Constructor for PinTBlockByBlock scheduler
        """
        super().__init__(taskPool=taskPool, nProc=nProc, nPoints=nPoints)

        # Use three list to divide tasks:
        #   - availableTasks: All prerequisites are fulfilled
        #   - notAvailableTasks: At least one prerequisite is not fulfilled
        #   - finishedTasks: Finished tasks
        self.availableTasks = set([key for key, value in self.taskPool.pool.items() if len(value.dep) == 0])
        self.notAvailableTasks = set([key for key, value in self.taskPool.pool.items() if len(value.dep) > 0])
        self.finishedTasks = set([])

    @abstractmethod
    def pickTask(self):
        """
        Abstract method
        Contains logic to pick the next task to schedule.
        """
        raise NotImplementedError()

    @abstractmethod
    def assignTask(self, taskName: sy.Symbol) -> None:
        """
        Abstract method for assigning task

        Parameters
        ----------
        taskName : sy.Symbol
            The name of the task to be scheduled
        """
        raise NotImplementedError()

    def updateLists(self, taskName: sy.Symbol) -> None:
        """
        Updates all three lists after task *taskName* is scheduled

        Parameters
        ----------
        taskName : sy.Symbol
            The name of the last scheduled task
        """
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

    def computeSchedule(self) -> None:
        """
        Main routine to compute a schedule.
        The scheduler is based on the following routine:

        As long as there are tasks that can be scheduled:
            - Choose one tasks based on logic (see pickTasks)
            - Assign task, i.e. compute the earliest possible start
              on the corresponding process
            - Update the three lists of tasks
        """
        while len(self.availableTasks) != 0:
            taskName = self.pickTask()
            self.assignTask(taskName=taskName)
            self.updateLists(taskName=taskName)

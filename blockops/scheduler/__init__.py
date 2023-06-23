import pkgutil
import numpy as np
from typing import Dict
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from abc import ABC, abstractmethod
import plotly.graph_objects as go

from blockops.utils.params import ParamClass, setParams
from blockops.utils.params import PositiveInteger, TaskPoolParam
from blockops.taskPool import TaskPool


class ScheduledTask:
    """
    Helper class containing information about scheduled task
    """

    def __init__(self, proc: int, start: float, end: float, name: str, color: str = 'gray') -> None:
        """
        Constructor for ScheduledTask

        Parameters
        ----------
        proc : int
            Process associated to this task
        start : float
            Start point
        end : float
            End point
        name : str
            Name of the task
        color : str
            Color of this task
        """
        self.proc = proc
        self.start = start
        self.name = name
        self.end = end
        self.color = color


@setParams(
    taskPool=TaskPoolParam(),
    nProc=PositiveInteger(),
    nPoints=PositiveInteger()
)
class Scheduler(ABC, ParamClass):
    """
    Base class for a scheduler (assigns start points to tasks)

    Parameters
    ----------
    taskPool : TaskPool
        Task pool containing all tasks to be scheduled
    nProc : int
        The number of processes
    nPoints : int
        The number of blocks
    """

    NAME = None  # unique name for the schedule
    IDS = set()  # list of ids that can be used for usage of this schedule

    def __init__(self, taskPool: TaskPool, nProc: int, nPoints: int) -> None:
        """
        Constructor for abstract scheduler class
        """
        self.schedule = {}
        self.taskPool = taskPool
        self.makespan = 0
        self.nProc = nProc
        self.startPointProc = np.zeros(self.nProc)
        self.nPoints = nPoints

    @abstractmethod
    def computeSchedule(self):
        """
        Abstract method.

        Child classes overwrites the method to define schedule
        """
        pass

    @staticmethod
    def getDefaultNProc(N):
        """Return a default number of processors for a given number of block"""
        return None

    def getRuntime(self) -> float:
        """
        Returns the runtime of a schedule

        Returns
        -------
            self.makespan : float
        Runtime of schedule
        """
        return self.makespan

    def plotPlotly(self) -> None:
        """
        Helper function to plot a schedule using plotly
        """
        fig = go.Figure(data=[],
                        layout=go.Layout(
                            titlefont_size=16,
                            showlegend=True,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                        )
                        )
        colors = {}
        maxRuntime = 0
        for key, value in self.schedule.items():
            time = value.end - value.start

            if value.color not in colors:
                colors[value.color] = [[],[], value.name, value.end - value.start, []]

            if value.end > maxRuntime:
                maxRuntime = value.end
            if time > 0:
                shapes_x = colors[value.color][0]
                shapes_y = colors[value.color][1]
                shapes_x.append(value.start)
                shapes_x.append(value.start+time)
                shapes_x.append(value.start+time)
                shapes_x.append(value.start)
                shapes_x.append(value.start)
                shapes_x.append(None)
                shapes_y.append(value.proc + .225)
                shapes_y.append(value.proc + .225)
                shapes_y.append(value.proc + .725)
                shapes_y.append(value.proc + .725)
                shapes_y.append(value.proc + .225)
                shapes_y.append(None)

        for key, value in colors.items():
            fig.add_trace(
                go.Scatter(
                    x=value[0],
                    y=value[1],
                    fill="toself",
                    fillcolor=key,
                    marker=dict(
                        color='black',
                        size=1,
                        line=dict(
                            color='black',
                            width=5
                        )
                    ),
                    hoverinfo='text',
                    text='Cost:'+str(value[3]),
                    name= value[2],
                    showlegend=True
                )
            )
        fig.update_xaxes(title="Time")
        fig.update_yaxes(title="Processor rank")
        fig.update_yaxes(
            ticktext=['P' + str(i) for i in range(self.nProc - 1, -1, -1)],
            tickvals=(np.linspace(self.nProc - 1, 0, self.nProc) + 0.5).tolist(),
        )
        fig.show()

    def plot(self, figName: str, figSize: tuple = (8, 4.8), saveFig: str = "") -> None:
        """
        Helper function to plot a schedule

        Parameters
        ----------
        figName : str
            Figure name
        figSize : tuple
            Figure size
        saveFig : str
            Saves the plot in the file *saveFig* if not equal to ""
        """
        fig, ax = plt.subplots(1, 1, figsize=figSize, num=figName)
        colors = {}
        for key, value in self.schedule.items():
            time = value.end - value.start
            if time > 0:
                operation = value.name
                rec = Rectangle((value.start, value.proc + .225), time, .5, color='k', fc=value.color)
                ax.add_patch(rec)
                if value.color not in colors:
                    colors[value.color] = operation
        ax.set_xlim(0, self.makespan)
        ax.set_ylim(0, self.nProc)
        ax.set_yticks(np.linspace(self.nProc - 1, 0, self.nProc) + 0.5)
        ax.set_yticklabels(['P' + str(i) for i in range(self.nProc - 1, -1, -1)])
        ax.set_ylabel(ylabel='Processor rank')
        ax.set_xlabel(xlabel='Computation cost')
        leg = [Line2D([0],
                      [0],
                      marker='o',
                      color='w',
                      label=value,
                      markerfacecolor=key,
                      markersize=15) for key, value in colors.items()]
        plt.legend(handles=leg,
                   title='Task description',
                   loc='upper center',
                   bbox_to_anchor=(0.5, 1.25),
                   ncol=5,
                   fancybox=True,
                   shadow=True,
                   numpoints=1,
                   fontsize=16)
        if saveFig != "":
            fig.savefig(saveFig, bbox_inches='tight', pad_inches=0.5)
        fig.show()


# Dictionary to store all the scheduler implementations
SCHEDULER: Dict[str, Scheduler] = {}


def register(cls: Scheduler) -> Scheduler:
    for stringID in cls.IDS:
        SCHEDULER[stringID] = cls
    return cls


# Import submodules to register Scheduler classes in SCHEDULER
__all__ = [name for name in locals().keys() if not name.startswith('__')]
for loader, moduleName, _ in pkgutil.walk_packages(__path__):
    __all__.append(moduleName)
    __import__(__name__ + '.' + moduleName)


def getSchedule(taskPool: TaskPool, nProc: int, nPoints: int, schedulerType: str) -> Scheduler:
    """
    Helper function to get scheduler and compute schedule

    Parameters
    ----------
    taskPool : str
        Figure name
    nProc: int, None
        Number of procs
    nPoints: int
        Number of blocks
    schedulerType: str
        Name of the scheduler

    Returns
    -------
    scheduler : Scheduler
        Scheduler containing schedule
    """
    SchedulerClass = SCHEDULER[schedulerType]
    nProc = SchedulerClass.getDefaultNProc(nPoints - 1) if nProc is None else nProc
    scheduler = SchedulerClass(taskPool=taskPool, nProc=nProc, nPoints=nPoints)
    scheduler.computeSchedule()
    return scheduler

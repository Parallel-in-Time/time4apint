# Python import

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from .graph import PintGraph

SCHEDULE_TYPES = {'BLOCK-BY-BLOCK': lambda graph, nProc, nPoints: PinTBlockByBlock(graph=graph, nProc=nProc, nPoints=nPoints),
                  'WINDOWING': lambda graph, nProc, nPoints: PinTWindowing(graph=graph, nProc=nProc, nPoints=nPoints),
                  'OPTIMAL': lambda graph, nProc, nPoints: Optimal(graph=graph, nProc=nProc, nPoints=nPoints)}

def getSchedule(graph : PintGraph, nProc : int, nPoints : int, schedule_type : str):
    if schedule_type not in SCHEDULE_TYPES:
        raise Exception(f"Schedule {type} not implemented, must be in {list(SCHEDULE_TYPES.keys())}")
    else:
        schedule = SCHEDULE_TYPES[schedule_type](graph=graph.graph, nProc=nProc, nPoints=nPoints)
        return schedule

class ScheduledTask():

    def __init__(self, proc, start, end, name):
        self.proc = proc
        self.start = start
        self.name = name
        self.end = end


class Schedule:

    def __init__(self, graph, nProc, nPoints):
        self.schedule = {}
        self.schedule_name = ''
        self.graph = graph
        self.makespan = 0
        self.nProc = nProc
        self.start_point_proc = np.zeros(self.nProc)
        self.nodes = list(graph.nodes(data=True))
        self.nPoints = nPoints

        self.computeSchedule()

    def computeSchedule(self):
        pass

    def getRuntime(self):
        return self.makespan

    def plot(self, figName):
        fig, ax = plt.subplots(1, 1, figsize=(8, 4.8), num=figName)
        for key, value in self.schedule.items():
            time = value.end - value.start
            if time > 0:
                operation = value.name
                color = 'gray'  # get_color(operation=operation, model=True, level=level)
                rec = Rectangle((value.start, value.proc + .225), time, .5, color='k', fc=color)
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

    def __init__(self, nPoints, nProc, *args: object, **kwargs: object):
        self.nPoints = nPoints
        self.nProc = nProc
        self.distribution = np.array([int(self.nPoints / self.nProc + 1)] * (self.nPoints % self.nProc) +
                                     [int(self.nPoints / self.nProc)] * (self.nProc - self.nPoints % self.nProc))
        self.point_to_proc = {}
        start = 0
        for i in range(self.nProc):
            for j in range(start, start + self.distribution[i]):
                self.point_to_proc[j] = i
            start += self.distribution[i]
        super().__init__(nPoints=nPoints, nProc=nProc, *args, **kwargs)
        self.schedule_name = '"PinT Block-by-Block"'

    def computeSchedule(self):
        counter = 0
        for item in self.nodes:
            possible_start_time = self.start_point_proc[self.point_to_proc[item[1]['point']]]
            if len(self.graph.in_edges(item[0])) == 0:
                possible_start_time = 0
            tmp_commu = 0
            for u, v, data in self.graph.in_edges(item[0], data=True):
                if self.schedule[u].end + data['cost'] > possible_start_time:
                    tmp_commu = data['cost']
                    possible_start_time = self.schedule[u].end + data['cost']
            # TODO add communication
            # if tmp_commu > 0:
            #    self.schedule['commu|' + str(counter)] = {'proc': self.point_to_proc[item[1]['point']],
            #                                         'start': possible_start_time - tmp_commu,
            #                                         'end': possible_start_time}
            #    counter += 1
            self.schedule[item[0]] = ScheduledTask(proc=self.point_to_proc[item[1]['point']],
                                                   start=possible_start_time,
                                                   end=possible_start_time + item[1]['cost'],
                                                   name=item[1]['name'])

            self.start_point_proc[self.point_to_proc[item[1]['point']]] = self.schedule[item[0]].end
            if self.schedule[item[0]].end > self.makespan:
                self.makespan = self.schedule[item[0]].end


class PinTWindowing(Schedule):

    def __init__(self, *args: object, **kwargs: object):
        raise Exception('not implemented')
        super().__init__(*args, **kwargs)
        self.schedule_name = '"PinTWindowing"'


# TODO: This is a first version, requires improvement
class Optimal(Schedule):
    """
    Calculates an optimal schedule using a simple greedy approach.
    Assumes unlimited processes and does not minimize the number of processes.
    """

    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)
        self.schedule_name = '"Optimal"'

    def computeSchedule(self):
        self.start_point_proc = np.zeros(20000000)
        for item in self.nodes:
            minimal_start_time = 0
            for u, v, data in self.graph.in_edges(item[0], data=True):
                if self.schedule[u].end > minimal_start_time:
                    minimal_start_time = self.schedule[u].end
            for i in range(len(self.start_point_proc)):
                if self.start_point_proc[i] <= minimal_start_time:
                    self.schedule[item[0]] = ScheduledTask(proc=i,
                                                           start=minimal_start_time,
                                                           end=minimal_start_time + item[1]['cost'],
                                                           name=item[1]['name'])
                    self.start_point_proc[i] = self.schedule[item[0]].end
                    break
            if self.schedule[item[0]].end > self.makespan:
                self.makespan = self.schedule[item[0]].end
        self.nProc = len(np.where(self.start_point_proc != 0)[0])

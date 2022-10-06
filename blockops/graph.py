# Python import
import re
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import Rectangle


# TODO:
# - Communication costs

class PintGraph:
    """DOCTODO"""

    # Constructor
    def __init__(self):
        """
        Creates a graph

        Parameters
        ----------
        """
        self.graph = nx.DiGraph()
        self.graph.add_node('u_0', pos=(0, -1), cost=0, name='init')
        self.pool = None

    def computeDependencies(self, pool):
        """Returns a restructured task pool for the creation of a plot"""
        newPool = {}
        for key, value in reversed(pool.items()):
            parts = re.split('_|\^', key.name)
            new_key = [int(parts[1]), int(parts[2])]
            size = len(parts)
            if size == 3:
                newPool[tuple(new_key)] = {'task': value, 'subtasks': [], 'oldkey': key}
            else:
                for j in range(3, size):
                    new_key.append(int(parts[j]))
                newPool[tuple(new_key[:-1])]['subtasks'].append(tuple(new_key))
                newPool[tuple(new_key)] = {'task': value, 'subtasks': [], 'oldkey': key}
        return newPool

    def computePos(self, pos, i, size):
        """Returns a position for a task"""
        diff = 0.3
        if i == 0:
            return (pos[0] - diff, pos[1])
        elif i == 1:
            return (pos[0] - diff, pos[1] - diff)
        else:
            return (pos[0] - diff + ((i - 1) * diff / (size - 1))), pos[1] - diff

    def addTaskToGraph(self, pos, task):
        """Adds task to the digraph. Previously recursively all subtasks"""
        old_key = task['oldkey'].name
        for i in range(len(task['subtasks'])):
            self.addTaskToGraph(pos=self.computePos(pos=pos, i=i, size=len(task['subtasks'])),
                                task=self.pool[task['subtasks'][i]])
        self.graph.add_node(old_key, pos=pos, name=f'${task["task"].name}$', cost=task['task'].cost)
        for item in task['task'].dep:
            self.graph.add_edge(item.name, old_key)

    def generateGraphFromPool(self, pool):
        """Creates graph vom taskpool"""
        self.pool = self.computeDependencies(pool=pool)
        for key, value in reversed(self.pool.items()):
            if len(key) == 2:
                self.addTaskToGraph(pos=key, task=value)

    def plotGraph(self):
        """Plots the graph"""
        plt.figure()
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'name'), with_labels=True)
        plt.show()

    def createEdgeWeightedGraph(self) -> nx.DiGraph:
        """Creates a graph with only edge weights to use the longest path algorithm"""
        newGraph = nx.DiGraph()
        trans = {}
        for node, node_data in self.graph.nodes(data=True):
            name1 = node + ".1"
            name2 = node + ".2"
            newGraph.add_node(name1, cost=0, pos=(node_data['pos'][0], node_data['pos'][1] - 0.001))
            newGraph.add_node(name2, cost=0, pos=(node_data['pos'][0], node_data['pos'][1] + 0.001))
            newGraph.add_edge(name1, name2, cost=node_data['cost'])
            trans[node] = [name1, name2]

        for edge_from, edge_to, edge_data in self.graph.edges(data=True):
            from_ = trans[edge_from][1]
            to_ = trans[edge_to][0]
            newGraph.add_edge(from_, to_, cost=edge_data['cost'])
        return newGraph

    def longestPath(self) -> float:
        """Computes longest path within the graph"""
        length = nx.dag_longest_path_length(self.graph)
        print('Longest path:', nx.dag_longest_path(self.graph))
        print('Longest path costs:', length)
        return length

    #TODO: This is a first version, requires improvement
    def computeOptimalSchedule(self, plot: bool) -> dict:
        """
        Calculates an optimal schedule using a simple greedy approach.
        Assumes unlimited processes and does not minimize the number of processes.

        :param plot: Plot the schedule
        :return: Schedule
        """
        print('Optimal schedule assumes unlimited resources and no communication costs')

        graph = self.graph

        schedule = {}
        nodes = list(graph.nodes(data=True))
        makespan = 0
        proc_start = np.zeros(20000000)
        counter = 0

        for item in nodes:
            minimal_start_time = 0
            for u, v, data in graph.in_edges(item[0], data=True):
                if schedule[u]['end'] > minimal_start_time:
                    minimal_start_time = schedule[u]['end']
            for i in range(len(proc_start)):
                if proc_start[i] <= minimal_start_time:
                    schedule[item[0]] = {'proc': i,
                                         'start': minimal_start_time,
                                         'end': minimal_start_time + item[1]['cost'],
                                         'name': item[1]['name']}
                    proc_start[i] = schedule[item[0]]['end']
                    break
            if schedule[item[0]]['end'] > makespan:
                makespan = schedule[item[0]]['end']

        required_procs = len(np.where(proc_start != 0)[0])
        print('Makespan of optimal schedule:', makespan, 'using', required_procs, 'processes')

        if plot:
            fig, (ax) = plt.subplots(1, 1, figsize=(8, 4.8))
            self.plotSchedule(schedule=schedule, ax=ax)
            ax.set_xlim(0, makespan)
            ax.set_ylim(0, required_procs)
            plt.yticks(np.linspace(required_procs - 1, 0, required_procs) + 0.5,
                       ['P' + str(i) for i in range(required_procs - 1, -1, -1)])
            plt.show()
        return schedule

    @staticmethod
    def plotSchedule(schedule: dict, ax: plt.axis) -> None:
        """
        Plots a schedule

        :param schedule: Schedule
        :param ax: Axis
        """
        for key, value in schedule.items():
            time = value['end'] - value['start']
            if time > 0:
                operation = value['name']
                color = 'gray'  # get_color(operation=operation, model=True, level=level)
                rec = Rectangle((value['start'], value['proc'] + .225), time, .25, color='k', fc=color)
                ax.add_patch(rec)
                rx, ry = rec.get_xy()
                cx = rx + rec.get_width() / 2.0
                cy = ry + rec.get_height() / 2.0
                ax.annotate(operation, (cx, cy), color='w', weight='bold',
                            fontsize=6, ha='center', va='center')

    #TODO: Not required so far, i think can be deleted
    def simplifyGraph(self):
        """Graph simplification"""
        rev_multidict = {}
        for key, value in self.pool.items():
            rev_multidict.setdefault(tuple(value[:2]), set()).add(key)
        for key, values in rev_multidict.items():
            if len(values) > 1:
                node = min(values)
                for item in values:
                    if item != node:
                        foll = list(self.graph.out_edges(item))
                        if len(foll[0]) > 1:
                            foll = list(foll[0])
                        for z in foll:
                            if z != item:
                                self.graph.add_edge(node, z)
                        self.graph.remove_node(item)

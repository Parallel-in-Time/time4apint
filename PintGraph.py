import re

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import Rectangle


# TODO:
# - Communication costs

class PintGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.graph.add_node('u_0', pos=(0, -1), cost=0, name='init')
        self.pool = None

    def generateGraphFromPool(self, pool):
        self.pool = pool
        last_subtask = None
        last_subsubtask = None
        for key, value in pool.items():
            parts = re.split('_|\^', key.name)
            n = int(parts[1])
            k = int(parts[2])
            if len(parts) > 3:
                subtask = int(parts[3])
            else:
                subtask = None
                last_subtask = None
            if subtask is None:
                pos = (n, k)
            else:
                if len(parts) > 4:
                    z = 3 - int(parts[4])
                    last_subsubtask = int(parts[4])
                else:
                    z = 0
                if last_subtask is None:
                    last_subtask = 1
                else:
                    last_subtask += 1
                    if last_subsubtask == 2:
                        last_subtask -=1
                if last_subtask == 1:
                    pos = (n - .4, k - .4)
                elif last_subtask == 2:
                    pos = (n - .4 - (z * 0.1), k)
                elif last_subtask == 3:
                    pos = (n - (z * 0.1), k - .4)
                else:
                    pos = (n, k - .4)
            self.graph.add_node(key.name, pos=pos, name=value.name, cost=value.cost)

            for item in value.dep:
                self.graph.add_edge(item.name, key.name)

    def plotGraph(self):
        plt.figure()
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'name'), with_labels=True)
        # nx.draw_planar(self.graph, labels=nx.get_node_attributes(self.graph, 'name'), with_labels=True, alpha=0.8)
        plt.show()

    def create_only_edge_weighted_graph(self) -> nx.DiGraph:
        """
        Creates a graph with only edge weights to use the longest path algorithm

        :return: Graph with only edge weights
        """
        new_graph = nx.DiGraph()
        trans = {}
        for node, node_data in self.graph.nodes(data=True):
            name1 = node + ".1"
            name2 = node + ".2"
            new_graph.add_node(name1, cost=0, pos=(node_data['pos'][0], node_data['pos'][1] - 0.001))
            new_graph.add_node(name2, cost=0, pos=(node_data['pos'][0], node_data['pos'][1] + 0.001))
            new_graph.add_edge(name1, name2, cost=node_data['cost'])
            trans[node] = [name1, name2]

        for edge_from, edge_to, edge_data in self.graph.edges(data=True):
            from_ = trans[edge_from][1]
            to_ = trans[edge_to][0]
            new_graph.add_edge(from_, to_, cost=edge_data['cost'])
        return new_graph

    def longest_path(self) -> float:
        """
        Computes longest path

        :return: Longest path length
        """
        length = nx.dag_longest_path_length(self.graph)
        print('Longest path:', nx.dag_longest_path(self.graph))
        print('Longest path costs:', length)
        return length

    def compute_optimal_schedule(self, plot: bool) -> dict:
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
            self.plot_schedule(schedule=schedule, ax=ax)
            ax.set_xlim(0, makespan)
            ax.set_ylim(0, required_procs)
            plt.yticks(np.linspace(required_procs - 1, 0, required_procs) + 0.5,
                       ['P' + str(i) for i in range(required_procs - 1, -1, -1)])
            plt.show()
        return schedule

    @staticmethod
    def plot_schedule(schedule: dict, ax: plt.axis) -> None:
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

    def simplify_graph(self):
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

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
    def __init__(self, nBlocks, maxK):
        """
        Creates a graph

        Parameters
        ----------
        """
        self.graph = nx.DiGraph()
        # self.graph.add_node('u_0_0', pos=(0, -1), cost=0, name='init')
        self.pool = None
        self.nBlocks = nBlocks
        self.maxK = maxK
        self.counter = 0
        self.lookup = {}

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
        for i in range(len(task['subtasks']) - 1, -1, -1):
            self.addTaskToGraph(pos=self.computePos(pos=pos, i=i, size=len(task['subtasks'])),
                                task=self.pool[task['subtasks'][i]])
        name = task["task"].name
        # name = task["task"].name if (
        #            f'{task["task"].name}'.startswith('$') and f'{task["task"].name}'.endswith('$')) else f'${task["task"].name}$'
        self.graph.add_node(self.counter, pos=pos, name=name, cost=task['task'].cost, op=task['task'].op_latex,
                            result=task['task'].result_latex, counter=self.counter)
        self.lookup[old_key] = self.counter
        for item in task['task'].dep:
            self.graph.add_edge(self.lookup[item.name], self.counter, cost=0)
        self.counter += 1

    def generateGraphFromPool(self, pool):
        """Creates graph vom taskpool"""
        self.pool = self.computeDependencies(pool=pool)
        for key, value in reversed(self.pool.items()):
            if len(key) == 2:
                self.addTaskToGraph(pos=key, task=value)

    def plotGraph(self, figName=None):
        """Plots the graph"""
        fig, ax = plt.subplots(num=figName)
        for k in range(self.maxK + 1):
            plt.axhline(y=k, color='gray', linestyle='-', alpha=0.3)
        for n in range(self.nBlocks + 1):
            plt.axvline(x=n, color='gray', linestyle='-', alpha=0.3)
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'name'), with_labels=True, ax=ax)
        limits = plt.axis('on')  # turns on axis
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        ax.set_xlim(left=-0.2, right=self.nBlocks + 0.2)
        ax.set_ylim(bottom=-.6, top=self.maxK + .2)
        ax.set_xlabel(xlabel='Time block n')
        ax.set_ylabel(ylabel='Iteration k')
        ax.set_xticks(ticks=np.arange(0, self.nBlocks + 1))
        ax.set_xticklabels(labels=np.arange(0, self.nBlocks + 1))
        ax.set_yticks(ticks=np.arange(0, self.maxK + 1))
        ax.set_yticklabels(labels=np.arange(0, self.maxK + 1))
        plt.show()

    def plotGraph2(self):
        G = self.graph
        fig, ax = plt.subplots()
        pos = nx.get_node_attributes(self.graph, 'pos')
        for k in range(self.maxK + 1):
            plt.axhline(y=k, color='gray', linestyle='-', alpha=0.3)
        for n in range(self.nBlocks + 1):
            plt.axvline(x=n, color='gray', linestyle='-', alpha=0.3)

        nodes = nx.draw_networkx_nodes(G, node_size=500, pos=pos, ax=ax,
                                       label=nx.get_node_attributes(self.graph, 'name'))
        nx.draw_networkx_edges(G, pos=pos, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(self.graph, 'name'))

        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        limits = plt.axis('on')  # turns on axis
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        ax.set_xlim(left=-0.2, right=self.nBlocks + 0.2)
        ax.set_ylim(bottom=-0.6, top=self.maxK + .2)
        ax.set_xlabel(xlabel='Time block n')
        ax.set_ylabel(ylabel='Iteration k')
        ax.set_xticks(ticks=np.arange(0, self.nBlocks + 1))
        ax.set_xticklabels(labels=np.arange(0, self.nBlocks + 1))
        ax.set_yticks(ticks=np.arange(0, self.maxK + 1))
        ax.set_yticklabels(labels=np.arange(0, self.maxK + 1))

        def update_annot(ind):
            node = ind["ind"][0]
            xy = pos[node]
            annot.xy = xy
            node_attr = {'node': node}
            node_attr.update(G.nodes[node])
            attr_list = ['name', 'cost', 'result', 'op', 'counter']
            text = '\n'.join(f'{k}: {v}' for k, v in node_attr.items() if k in attr_list)
            annot.set_text(text)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = nodes.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        plt.show()

    def createEdgeWeightedGraph(self) -> nx.DiGraph:
        """Creates a graph with only edge weights to use the longest path algorithm"""
        newGraph = nx.DiGraph()
        trans = {}
        for node, node_data in self.graph.nodes(data=True):
            name1 = f'{node}' + ".1"
            name2 = f'{node}' + ".2"
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
        gra = self.createEdgeWeightedGraph()
        length = nx.dag_longest_path_length(gra, weight="cost")
        # print('Longest path:', nx.dag_longest_path(gra, weight="cost"))
        # print('Longest path costs:', length)
        return length

    # TODO: This is a first version, requires improvement
    def computeOptimalSchedule(self, plot: bool, figName=None) -> dict:
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
            fig, ax = plt.subplots(1, 1, figsize=(8, 4.8), num=figName)
            self.plotSchedule(schedule=schedule, ax=ax)
            ax.set_xlim(0, makespan)
            ax.set_ylim(0, required_procs)
            ax.set_yticks(
                np.linspace(required_procs - 1, 0, required_procs) + 0.5,
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

    # TODO: Not required so far, i think can be deleted
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

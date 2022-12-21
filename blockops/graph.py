# Python import
import copy
import re

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# TODO
# - Communication costs

COLOR_LIST = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974',
              '#64b5cd']


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
        self.pool = None
        self.nBlocks = nBlocks
        self.maxK = maxK
        self.counter = 0
        self.lookup = {}

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
        for i in range(len(task.subtasks)):
            self.addTaskToGraph(pos=self.computePos(pos=pos, i=i, size=len(task.subtasks)),
                                task=self.pool.getTask(task.subtasks[i]))
        self.graph.add_node(self.counter, pos=pos, task=task, name=task.name)
        self.lookup[task.result] = self.counter
        for item in task.dep:
            self.graph.add_edge(self.lookup[self.pool.getTask(item).result], self.counter, cost=0)
        self.counter += 1

    def generateGraphFromPool(self, pool):
        """Creates graph vom taskpool"""
        self.pool = pool
        for key, value in self.pool.pool.items():
            if value.type == 'main':
                self.addTaskToGraph(pos=(value.block, value.iteration), task=value)

    def plotGraph(self, figName=None):
        """Plots the graph"""
        fig, ax = plt.subplots(num=figName)
        for k in range(self.maxK + 1):
            plt.axhline(y=k, color='gray', linestyle='-', alpha=0.3)
        for n in range(self.nBlocks + 1):
            plt.axvline(x=n, color='gray', linestyle='-', alpha=0.3)
        pos = nx.get_node_attributes(self.graph, 'pos')
        color = [node[1]['task'].color for node in self.graph.nodes(data=True)]
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'name'), with_labels=True, ax=ax,
                node_color=color)
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

    def longestPath(self) -> float:
        """Computes longest path within the graph"""
        newGraph = nx.DiGraph()
        trans = {}
        for node, node_data in self.graph.nodes(data=True):
            name1 = f'{node}' + ".1"
            name2 = f'{node}' + ".2"
            newGraph.add_node(name1, cost=0, pos=(node_data['pos'][0], node_data['pos'][1] - 0.001))
            newGraph.add_node(name2, cost=0, pos=(node_data['pos'][0], node_data['pos'][1] + 0.001))
            newGraph.add_edge(name1, name2, cost=node_data['task'].cost)
            trans[node] = [name1, name2]

        for edge_from, edge_to, edge_data in self.graph.edges(data=True):
            from_ = trans[edge_from][1]
            to_ = trans[edge_to][0]
            newGraph.add_edge(from_, to_, cost=edge_data['cost'])
        length = nx.dag_longest_path_length(newGraph, weight="cost")
        return length

# Python import
import copy
import re
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# TODO
# - Communication costs

COLOR_LIST = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974',
              '#64b5cd']


class Position:

    def __init__(self, nBlocks, k):

        self.a = np.array([[0 for x in range(nBlocks+1)] for y in range(k+1)])

    def getPosition(self, n,k):
        pos = [(-.8,-.8),(-.6,-.8),(-.4,-.8),(-.2,-.8),(-.8,-.6),(-.6,-.6),(-.4,-.6),(-.2,-.6),
               (-.8,-.4),(-.6,-.4),(-.4,-.4),(-.2,-.4),(-.8,-.2),(-.6,-.2),(-.4,-.2),(-.2,-.2)]
        idx = self.a[n][k]
        self.a[n][k] += 1
        pos = (n+pos[idx][0],k+pos[idx][1])
        return pos


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
        self.edges = []
        self.pos = Position(nBlocks=nBlocks,k=maxK)

    def computePos(self, pos, i, size):
        """Returns a position for a task"""
        diff = 0.4
        if i == 0:
            return (pos[0] - diff, pos[1] -.5)
        elif i == 1:
            return (pos[0] - diff, pos[1] - diff-.3)
        else:
            return (pos[0] - diff + ((i - 1) * diff / (size - 1))), pos[1] - diff

    def addTaskToGraph(self, pos, task):
        """Adds task to the digraph. Previously recursively all subtasks"""
        # for i in range(len(task.subtasks)):
        #     self.addTaskToGraph(pos=self.computePos(pos=pos, i=i, size=len(task.subtasks)),
        #                         task=self.pool.getTask(task.subtasks[i]))
        res = ""
        if task.type == 'main':
            res = f'${str(task.result)}$'
        self.graph.add_node(self.counter, pos=pos, task=task, res=res)
        self.lookup[task.result] = self.counter
        # for item in task.dep:
        self.edges.append((self.counter, task.dep))
            # self.graph.add_edge(self.lookup[self.pool.getTask(item).result], self.counter, cost=0)
        self.counter += 1

    def generateGraphFromPool(self, pool):
        """Creates graph vom taskpool"""
        self.pool = pool
        for key, value in self.pool.pool.items():
            if value.type == 'main':
                self.addTaskToGraph(pos=(value.block, value.iteration), task=value)
            else:
                #pos = self.pos.getPosition(value.block, value.iteration)
                pos = (value.block-.5, value.iteration-.5)
                self.addTaskToGraph(pos=pos, task=value)
        for item in self.edges:
            for dep in item[1]:
                self.graph.add_edge(self.lookup[self.pool.getTask(dep).result], item[0], cost=0)
    def plotGraph(self, figName=None, figSize=(6.4, 4.8)):
        """Plots the graph"""
        fig, ax = plt.subplots(num=figName, figsize=figSize)
        for k in range(self.maxK + 1):
            plt.axhline(y=k, color='gray', linestyle='-', alpha=0.3)
        for n in range(self.nBlocks + 1):
            plt.axvline(x=n, color='gray', linestyle='-', alpha=0.3)
        pos = nx.get_node_attributes(self.graph, 'pos')
        color = [node[1]['task'].color for node in self.graph.nodes(data=True)]
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'res'), with_labels=True, ax=ax,
                node_color=color, node_size=20, width=.5)
        leg = [Line2D([0], [0], marker='o', color='w', label=key,
                            markerfacecolor=value, markersize=15) for key, value in self.pool.colorLookup.items()]
        limits = plt.axis('on')  # turns on axis
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        ax.set_xlim(left=-0.2, right=self.nBlocks + 0.2)
        ax.set_ylim(bottom=-.6, top=self.maxK + .2)
        ax.set_xlabel(xlabel='Time block n')
        ax.set_ylabel(ylabel='Iteration k')
        ax.set_xticks(ticks=np.arange(-1, self.nBlocks + 1))
        ax.set_xticklabels(labels=np.arange(-1, self.nBlocks + 1))
        ax.set_yticks(ticks=np.arange(-1, self.maxK + 1))
        ax.set_yticklabels(labels=np.arange(-1, self.maxK + 1))
        plt.legend(handles=leg, title='Task description',loc='upper center', bbox_to_anchor=(0.5, 1.17),
          ncol=5, fancybox=True, shadow=True, numpoints = 1)
        fig.savefig('PFASSTTaskGraph.pdf', bbox_inches='tight', pad_inches=0.5)
        plt.show()

    def plotGraph2(self, figName=None, figSize=(6.4, 4.8)):
        """Plots the graph"""
        fig, ax = plt.subplots(num=figName, figsize=figSize)
        for k in range(self.maxK + 1):
            plt.axhline(y=k, color='gray', linestyle='-', alpha=0.3)
        for n in range(self.nBlocks + 1):
            plt.axvline(x=n, color='gray', linestyle='-', alpha=0.3)
        pos = nx.get_node_attributes(self.graph, 'pos')
        pos[0] = (0,0)
        pos[1] = (0.2,0)
        pos[2] = (0.4,0)
        pos[3] = (0.6,0)
        pos[4] = (.8,0)
        pos[5] = (1,0)
        pos[6] = (1.2,0)
        pos[7] =  (1.4,0.0)
        pos[8] =  (1.6,0)
        pos[9] =  (1.8,0)
        pos[10] = (2,0)
        pos[11] = (1,0.5)
        pos[12] = (0.8,0.5)
        pos[13] = (0.2,0.5)
        pos[14] = (.4,.7)
        pos[15] = (.4,0.85)
        pos[16] = (.6,.85)
        pos[17] = (.6,1)
        pos[18] = (1,1)
        pos[19] = (1.8,0.5)
        pos[20] = (1.2,.5)
        pos[21] = (1.2,1)
        pos[22] = (1.4,0.7)
        pos[23] = (1.4,0.85)
        pos[24] = (1.6,.85)
        pos[25] = (1.6,1)
        pos[26] = (2,1)
        color = [node[1]['task'].color for node in self.graph.nodes(data=True)]
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'res'), with_labels=True, ax=ax,
                node_color=color, node_size=260, width=.5)
        leg = [Line2D([0], [0], marker='o', color='w', label=key,
                            markerfacecolor=value, markersize=15) for key, value in self.pool.colorLookup.items() if value in color]
        limits = plt.axis('on')  # turns on axis
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        ax.set_xlim(left=-0.2, right=self.nBlocks + 0.2)
        ax.set_ylim(bottom=-.3, top=self.maxK + .2)
        ax.set_xlabel(xlabel='Time block n')
        ax.set_ylabel(ylabel='Iteration k')
        ax.set_xticks(ticks=np.arange(0, self.nBlocks + 1))
        ax.set_xticklabels(labels=np.arange(0, self.nBlocks + 1))
        ax.set_yticks(ticks=np.arange(0, self.maxK + 1))
        ax.set_yticklabels(labels=np.arange(0, self.maxK + 1))
        plt.legend(handles=leg, title='Task description',loc='upper center', bbox_to_anchor=(0.5, 1.3),
          ncol=5, fancybox=True, shadow=True, numpoints = 1)
        fig.savefig('PFASSTTaskGraph.pdf', bbox_inches='tight', pad_inches=0.5)
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

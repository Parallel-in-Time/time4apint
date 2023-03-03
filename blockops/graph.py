# Python import
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


# TODO
# - Communication costs

class Position:
    """
    Helper class to plot nodes non-overlapping.
    """

    def __init__(self, nBlocks, k):
        self.posIdx = np.array([[0 for _ in range(nBlocks + 1)] for _ in range(k + 1)])

    def getPosition(self, n, k):
        pos = [(-.8, -.85), (-.6, -.75), (-.4, -.85), (-.2, -.75),
               (-.8, -.65), (-.6, -.55), (-.4, -.65), (-.2, -.55),
               (-.8, -.45), (-.6, -.35), (-.4, -.45), (-.2, -.35),
               (-.8, -.25), (-.6, -.15), (-.4, -.25), (-.2, -.15)
               ]
        idx = self.posIdx[k][n]
        if idx < len(pos):
            pos = (n + pos[idx][0], k + pos[idx][1])
        else:
            pos = (np.random.random(1)[0], np.random.random(1)[0])
        self.posIdx[k][n] += 1
        return pos


class PintGraph:
    """DOCTODO"""

    # Constructor
    def __init__(self, nBlocks, maxK, taskPool):
        """
        Creates a graph

        Parameters
        ----------
        """
        self.graph = nx.DiGraph()
        self.pool = taskPool
        self.nBlocks = nBlocks
        self.maxK = maxK
        self.counter = 0
        self.lookup = {}
        self.pos = Position(nBlocks=nBlocks, k=maxK)
        self.generateGraphFromPool()

    def addTaskToGraph(self, pos, task):
        """Adds task to the digraph."""
        # Set name only for main tasks
        res = ""
        if task.type == 'main':
            res = f'${str(task.result)}$'
        # Add node
        self.graph.add_node(self.counter, pos=pos, task=task, res=res)
        self.lookup[task.result] = self.counter
        # Add dependencies
        for item in task.dep:
            self.graph.add_edge(self.lookup[self.pool.getTask(item).result], self.counter, cost=0)
        self.counter += 1

    def generateGraphFromPool(self):
        """Creates graph vom taskpool"""
        for key, value in self.pool.pool.items():
            if value.type == 'main':
                # Put u_x^y tasks (main tasks) on exact positions
                self.addTaskToGraph(pos=(value.block, value.iteration), task=value)
            else:
                # Put subtasks of u_x_y on specific positions
                self.addTaskToGraph(pos=self.pos.getPosition(value.block, value.iteration), task=value)

    def plotGraph(self, figName: str = "", figSize: tuple = (6.4, 4.8), saveFig: str = ""):
        """Plots the graph"""
        fig, ax = plt.subplots(num=figName, figsize=figSize)
        for k in range(self.maxK + 1):
            plt.axhline(y=k, color='gray', linestyle='-', alpha=0.3)
        for n in range(self.nBlocks + 1):
            plt.axvline(x=n, color='gray', linestyle='-', alpha=0.3)
        pos = nx.get_node_attributes(self.graph, 'pos')
        color = [node[1]['task'].color for node in self.graph.nodes(data=True)]
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'res'), with_labels=True, ax=ax,
                node_color=color, node_size=50, width=.5)
        leg = [Line2D([0], [0], marker='o', color='w', label=key, markerfacecolor=value, markersize=15)
               for key, value in self.pool.colorLookup.items() if value in color]
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
        plt.legend(handles=leg, title='Task description', loc='upper center', bbox_to_anchor=(0.5, 1.17),
                   ncol=5, fancybox=True, shadow=True, numpoints=1)
        if saveFig != "":
            fig.savefig(saveFig, bbox_inches='tight', pad_inches=0.5)
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

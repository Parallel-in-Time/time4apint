# Python import
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from blockops.taskPool import TaskPool, Task


# TODO
# - Communication costs

class Position:
    """
    Helper class to plot nodes non-overlapping.
    """

    def __init__(self, nBlocks: int, k: int) -> None:
        """
        Constructor

        Parameters
        ----------
        nBlocks : int
            Number of blocks
        k : int
            Iteration
        """
        # Index array
        self.posIdx = np.array([[0 for _ in range(nBlocks + 1)] for _ in range(k + 1)])
        # Positions
        self.pos = [(-.8, -.85), (-.6, -.75), (-.4, -.85), (-.2, -.75),
                    (-.8, -.65), (-.6, -.55), (-.4, -.65), (-.2, -.55),
                    (-.8, -.45), (-.6, -.35), (-.4, -.45), (-.2, -.35),
                    (-.8, -.25), (-.6, -.15), (-.4, -.25), (-.2, -.15)
                    ]

    def getPosition(self, n: int, k: int) -> tuple:
        """
        Constructor

        Parameters
        ----------
        n : int
            Block
        k : int
            Iteration

        Returns
        ----------
        nodePos : tuple
            Position of the node
        """
        idx = self.posIdx[k][n]
        if idx < len(self.pos):
            nodePos = (n + self.pos[idx][0], k + self.pos[idx][1])
        else:
            nodePos = (np.random.random(1)[0], np.random.random(1)[0])
        self.posIdx[k][n] += 1
        return nodePos


class PintGraph:
    """
    Class representing the task graph associated for the taskpool of one Pint run
    """

    # Constructor
    def __init__(self, nBlocks: int, maxK: int, taskPool: TaskPool) -> None:
        """
        Creates a graph

        Parameters
        ----------
        nBlocks : int
            Number of blocks
        maxK : int
            Maximum number of iterations over all blocks
        taskPool : Taskpool
           Task pool to represent as graph
        """
        self.graph = nx.DiGraph()  # Graph
        self.pool = taskPool  # Pool
        self.nBlocks = nBlocks  # Number of blocks
        self.maxK = maxK  # Maximum number of iterations over all blocks
        self.counter = 0  # Helper to have unique names per node
        self.lookup = {}  # Lookup counter to task
        self.pos = Position(nBlocks=nBlocks, k=maxK)  # Helper to get position of tasks
        self.generateGraphFromPool()  # Generate graph from pool

    def addTaskToGraph(self, pos: tuple, task: Task) -> None:
        """
        Adds task to the digraph.

        Parameters
        ----------
        pos : tuple
            Position for this node
        task: Task
            Task which is represented by node
        """
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

    def generateGraphFromPool(self) -> None:
        """
        Creates graph vom taskpool
        """
        for key, value in self.pool.pool.items():
            if value.type == 'main':
                # Put u_x^y tasks (main tasks) on exact positions
                self.addTaskToGraph(pos=(value.block, value.iteration), task=value)
            else:
                # Put subtasks of u_x_y on specific positions
                self.addTaskToGraph(pos=self.pos.getPosition(value.block, value.iteration), task=value)

    def plotGraph(self, figName: str = "", figSize: tuple = (6.4, 4.8), saveFig: str = ""):
        """
        Plots the graph

        Parameters
        ----------
        figName : str
            Name of the figure
        figSize: tuple
            Figure size
        saveFig : str
            Save figure to path represented by str. No saving if str == ""
        """

        # Setup graph
        fig, ax = plt.subplots(num=figName, figsize=figSize)
        for k in range(self.maxK + 1):
            plt.axhline(y=k, color='gray', linestyle='-', alpha=0.3)
        for n in range(self.nBlocks + 1):
            plt.axvline(x=n, color='gray', linestyle='-', alpha=0.3)
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

        # Add nodes
        pos = nx.get_node_attributes(self.graph, 'pos')
        color = [node[1]['task'].color for node in self.graph.nodes(data=True)]
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'res'), with_labels=True, ax=ax,
                node_color=color, node_size=50, width=.5)

        # Add legend
        leg = [Line2D([0], [0], marker='o', color='w', label=key, markerfacecolor=value, markersize=15)
               for key, value in self.pool.colorLookup.items() if value in color]
        plt.legend(handles=leg, title='Task description', loc='upper center', bbox_to_anchor=(0.5, 1.17),
                   ncol=5, fancybox=True, shadow=True, numpoints=1)

        # Save to file
        if saveFig != "":
            fig.savefig(saveFig, bbox_inches='tight', pad_inches=0.5)

        plt.show()

    def longestPath(self) -> float:
        """
        Computes the longest path within the graph

        Returns
        ----------
        length : float
            Longest path within graph
        """

        # Translate to graph with only edge costs
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

        # Compute the longest path of new graph
        length = nx.dag_longest_path_length(newGraph, weight="cost")
        return length

# Python import
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from math import floor, ceil
import plotly.graph_objects as go

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
        self.maxK = min(maxK, self.pool.maxIter)  # Maximum number of iterations over all blocks
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

    def plotGraphForOneBlock(self, k: int, n: int, figName: str = "", figSize: tuple = (6.4, 4.8), saveFig: str = ""):
        """
        Plots subgraph containing only nodes for one given block and iteration

        Parameters
        ----------
        k  : int
            Iteration to plot
        n : int
            Block to plot
        figName : str
            Name of the figure
        figSize: tuple
            Figure size
        saveFig : str
            Save figure to path represented by str. No saving if str == ""
        """
        fig, ax = plt.subplots(num=figName, figsize=figSize)

        # Compute subgraph
        tasks = nx.get_node_attributes(self.graph, 'task')
        a = {}
        nodes = set()
        for key, value in tasks.items():
            if value.block == n and value.iteration == k:
                nodes.add(key)
                for item in value.dep:
                    nodes.add(a[item])

            a[value.result] = key
        sub = self.graph.subgraph(nodes)
        pos = nx.get_node_attributes(sub, 'pos')
        labels = nx.get_node_attributes(sub, 'res')
        color = [node[1]['task'].color for node in sub.nodes(data=True)]

        # Compute boundaries of graph
        minx = min([floor(value[0]) for key, value in pos.items()])
        miny = min([floor(value[1]) for key, value in pos.items()])
        maxx = max([ceil(value[0]) for key, value in pos.items()])
        maxy = max([ceil(value[1]) for key, value in pos.items()])

        # Plot subgraph
        nx.draw_networkx(sub, pos, labels=labels, with_labels=True, ax=ax,
                         node_color=color, node_size=50, width=.5)

        # Add legend
        leg = [Line2D([0], [0], marker='o', color='w', label=key, markerfacecolor=value, markersize=15)
               for key, value in self.pool.colorLookup.items() if value in color]
        plt.legend(handles=leg, title='Task description', loc='upper center', bbox_to_anchor=(0.5, 1.17),
                   ncol=5, fancybox=True, shadow=True, numpoints=1)

        limits = plt.axis('on')  # turns on axis
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        ax.set_xlabel(xlabel='Time block n')
        ax.set_ylabel(ylabel='Iteration k')
        ax.set_xticks(ticks=np.arange(minx, maxx + 1))
        ax.set_xticklabels(labels=np.arange(minx, maxx + 1))
        ax.set_yticks(ticks=np.arange(miny, maxy + 1))
        ax.set_yticklabels(labels=np.arange(miny, maxy + 1))
        plt.grid()

        # Save to file
        if saveFig != "":
            fig.savefig(saveFig, bbox_inches='tight', pad_inches=0.5)

        plt.show()

    def plotGraphForOneBlockPlotly(self, k: int, n: int):
        """
        Plots subgraph containing only nodes for one given block and iteration

        Parameters
        ----------
        k  : int
            Iteration to plot
        n : int
            Block to plot
        figName : str
            Name of the figure
        figSize: tuple
            Figure size
        saveFig : str
            Save figure to path represented by str. No saving if str == ""
        """

        # Compute subgraph
        tasks = nx.get_node_attributes(self.graph, 'task')
        a = {}
        nodes = set()
        for key, value in tasks.items():
            if value.block == n and value.iteration == k:
                nodes.add(key)
                for item in value.dep:
                    nodes.add(a[item])

            a[value.result] = key

        self.plotGraphPlotly(graph=self.graph.subgraph(nodes))
        return

    def plotGraphPlotly(self, graph = None):
        """
        Plots the graph using plotly
        """
        if graph is None:
            graph = self.graph
        edge_x = []
        edge_y = []
        for edge in graph.edges():
            x0, y0 = graph.nodes[edge[0]]['pos']
            x1, y1 = graph.nodes[edge[1]]['pos']
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            marker=dict(size=10, symbol="arrow-bar-up", angleref="previous"),
            mode='lines+markers')

        fig = go.Figure(data=[edge_trace],
                        layout=go.Layout(
                            titlefont_size=16,
                            showlegend=True,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                        )
                        )

        node_x = []
        node_y = []
        col = []
        for node in graph.nodes():
            x, y = graph.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)
            col.append(graph.nodes[node]['task'].color)

        color = [node[1]['task'].color for node in graph.nodes(data=True)]
        node_text = [node[1]['res'] for node in graph.nodes(data=True)]
        inv_map = {v: k for k, v in self.pool.colorLookup.items()}
        for c in set(color):
            x_new = [node_x[j] for j in range(len(col)) if col[j] == c]
            y_new = [node_y[j] for j in range(len(col)) if col[j] == c]
            text_new = [node_text[j] for j in range(len(col)) if col[j] == c]
            fig.add_trace(
                go.Scatter(
                    x=x_new,
                    y=y_new,
                    hoverinfo='text',
                    marker=dict(
                        color=c,
                        size=10,
                        line_width=2),
                    text=text_new,
                    name= inv_map[c],
                    mode='markers',
                    showlegend=True
                )
            )
        labels_to_show_in_legend = [inv_map[item] for item in set(color)]

        for trace in fig['data']:
            if (not trace['name'] in labels_to_show_in_legend):
                trace['showlegend'] = False

        fig.update_xaxes(title="Time block n")
        fig.update_yaxes(title="Iteration k")

        fig.show()

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
        plt.grid()

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

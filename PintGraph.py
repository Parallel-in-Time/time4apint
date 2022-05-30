import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import sympy
from matplotlib.patches import Rectangle
from copy import deepcopy

class PintGraph:
    """
    Base class for PinT task graphs
    """

    def __init__(self, iters: list, nt: int, cost_commu: float = 0, cost_local_conv_crit: float = 0,
                 cost_global_conv_crit: float = 0, conv_crit: int = 0, node_cost_only: bool = False) -> None:

        # Class variables
        self.cost_commu = cost_commu  # Cost per communication
        self.iterations = iters  # Number of iterations
        self.node_counter = 0  # Counter for nodes
        self.nt = nt  # Number of time point
        self.graph = nx.DiGraph()  # Task graph

        self.task_set = {}
        self.dependency_to_task = {}

        # Start node
        self.add_node(op='Initial_node',
                      predecessors=[],
                      set_values=['init_node'],
                      pos=[self.nt / 2, -2],
                      cost=0,
                      point=0)

        # Node representing the initial condition
        self.add_node(op='u_0',
                      predecessors=['init_node'],
                      set_values=['u_0'],
                      pos=[self.nt / 2 - 1, -1],
                      cost=0,
                      point=0)

        # Node representing the value zero
        self.add_node(op='0',
                      predecessors=['init_node'],
                      set_values=['0'],
                      pos=[self.nt / 2 + 1, -1],
                      cost=0,
                      point=0)

    def add_node(self, op: str, predecessors: list, set_values: list, cost: float, point: int, pos) -> None:
        name1 = op + "|" + str(self.node_counter)
        self.task_set[self.node_counter] = [op, tuple(predecessors), set_values]

        self.graph.add_node(self.node_counter, pos=(pos[0], pos[1]), point=point, weight=cost, name=name1)

        for item in predecessors:
            if isinstance(item, sympy.Symbol):
                qw = item.name
            else:
                qw = item
            self.graph.add_edge(self.dependency_to_task[qw], self.node_counter, weight=0)

        for item in set_values:
            self.dependency_to_task[item] = self.node_counter

        self.node_counter += 1

    def plot_dag(self, with_edge_weights: bool = False) -> None:
        """
        Plots the graph
        :param with_edge_weights:
        """
        plt.figure()
        for i in range(self.nt):
            plt.axvline(x=i + 0.5)
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos, labels=nx.get_node_attributes(self.graph, 'name'), with_labels=True)
        if with_edge_weights:
            edge_labels = dict([((n1, n2), f'{n3["weight"]}')
                                for n1, n2, n3 in self.graph.edges(data=True)])

            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
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
            new_graph.add_node(name1, weight=0, pos=(node_data['pos'][0], node_data['pos'][1] - 0.001),
                               desc=node_data['desc'], point=node_data['point'])
            new_graph.add_node(name2, weight=0, pos=(node_data['pos'][0], node_data['pos'][1] + 0.001),
                               desc=node_data['desc'], point=node_data['point'])
            new_graph.add_edge(name1, name2, weight=node_data['weight'])
            trans[node] = [name1, name2]

        for edge_from, edge_to, edge_data in self.graph.edges(data=True):
            from_ = trans[edge_from][1]
            to_ = trans[edge_to][0]
            new_graph.add_edge(from_, to_, weight=edge_data['weight'])
        return new_graph

    def longest_path(self) -> float:
        """
        Computes longest path

        :return: Longest path length
        """
        if not self.node_cost_only:
            print('Convert graph to a graph with only node costs. May take some time.')
            graph = self.create_only_edge_weighted_graph()
        else:
            graph = self.graph
        length = nx.dag_longest_path_length(graph)
        print('Longest path:', nx.dag_longest_path(graph))
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
                                         'end': minimal_start_time + item[1]['weight']}
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

    def compute_standard_schedule(self, procs: int, with_communication_costs: bool = False,
                                  plot: bool = False) -> object:
        """
        Computes standard schedule based on block-by-block basis

        :param procs: Number of processes
        :param with_communication_costs: Include communication costs?
        :param plot: Plot the schedule
        :return: Schedule and makespan
        """
        distribution = np.array([int(self.nt / procs + 1)] * (self.nt % procs) +
                                [int(self.nt / procs)] * (procs - self.nt % procs))
        point_to_proc = {}
        start = 0
        for i in range(procs):
            for j in range(start, start + distribution[i]):
                point_to_proc[j] = i
            start += distribution[i]

        if with_communication_costs:
            graph = deepcopy(self.graph)
            for u, v, a in graph.edges(data=True):
                from_ = graph.nodes[u]['point']
                to_ = graph.nodes[v]['point']
                if from_ != -99 and to_ != -99 and point_to_proc[from_] != point_to_proc[to_]:
                    if a["weight"] > 0:
                        raise Exception
                    a["weight"] = self.cost_commu
                else:
                    a["weight"] = 0
        else:
            graph = self.graph

        schedule = {}
        nodes = list(graph.nodes(data=True))
        makespan = 0
        proc_start = np.zeros(procs)
        counts_operation_per_proc = [{} for _ in range(procs)]
        counter = 0

        for item in nodes:
            possible_start_time = proc_start[point_to_proc[item[1]['point']]]
            if len(graph.in_edges(item[0])) == 0:
                possible_start_time = 0
            tmp_commu = 0
            for u, v, data in graph.in_edges(item[0], data=True):
                if schedule[u]['end'] + data['weight'] > possible_start_time:
                    tmp_commu = data['weight']
                    possible_start_time = schedule[u]['end'] + data['weight']
            if tmp_commu > 0:
                schedule['commu|' + str(counter)] = {'proc': point_to_proc[item[1]['point']],
                                                     'start': possible_start_time - tmp_commu,
                                                     'end': possible_start_time}
                counter += 1
            schedule[item[0]] = {'proc': point_to_proc[item[1]['point']],
                                 'start': possible_start_time,
                                 'end': possible_start_time + item[1]['weight']}
            op = '|'.join(item[0].split('|')[:-1])
            if item[1]['desc'] not in counts_operation_per_proc[point_to_proc[item[1]['point']]]:
                counts_operation_per_proc[point_to_proc[item[1]['point']]][item[1]['desc']] = 1
            else:
                counts_operation_per_proc[point_to_proc[item[1]['point']]][item[1]['desc']] += 1
            proc_start[point_to_proc[item[1]['point']]] = schedule[item[0]]['end']
            if schedule[item[0]]['end'] > makespan:
                makespan = schedule[item[0]]['end']

        print('Makespan of standard schedule:', makespan)

        if plot:
            fig, (ax) = plt.subplots(1, 1, figsize=(8, 4.8))
            self.plot_schedule(schedule=schedule, ax=ax)
            ax.set_xlim(0, makespan)
            ax.set_ylim(0, procs)
            # ax.legend(handles=list(save_ops.values()), loc='upper center', bbox_to_anchor=(0.5, 1.1),
            #           ncol=3, fancybox=True, shadow=True)
            plt.yticks(np.linspace(procs - 1, 0, procs) + 0.5,
                       ['P' + str(i) for i in range(procs - 1, -1, -1)])
            plt.show()
        return schedule, makespan

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
                operation = key.split('|')[0]
                level = int(key.split('|')[1])
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
        for key, value in self.task_set.items():
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
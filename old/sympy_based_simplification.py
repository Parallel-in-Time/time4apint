import sympy as sy
from PintGraph import PintGraph

f, g = sy.symbols('f,g', commutative=False)
null = f * 0

class NameGenerator(object):

    def __init__(self, prefix):
        self.prefix = prefix
        self.counter = 0

    def get(self):
        name = f'{"u" if self.counter == 0 else "v"}_{self.counter}'
        self.counter += 1
        return name


class SympyBasedApproach(PintGraph):
    def __init__(self, cost_fine: float, cost_coarse: float, cost_copy: float = 0, cost_correction: float = 0,
                 simplify_graph = True,*args: object, **kwargs: object) -> None:
        """
        Constructor

        :param cost_fine: Cost of the fine propagator
        :param cost_coarse: Cost of the coarse propagator
        :param cost_copy: Cost of a copy operation
        :param cost_correction: Cost of a correction
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.cost_coarse = cost_coarse
        self.cost_fine = cost_fine
        self.cost_correction = cost_correction
        self.cost_copy = cost_copy
        self.sim_graph = simplify_graph

        self.blockOperators = [
            {"dep": (-1, -1),
             "sym": f,
             },
            {"dep": (-1, -1),
             "sym": -g,
             },
            {"dep": (-1, 0),
             "sym": g,
             }]
        self.dico = {}

    def node(self, n, k):
        if k > self.iterations[n]:
            return sy.symbols(f'u_{n}^{self.iterations[n]}', commutative=False)
        else:
            return sy.symbols(f'u_{n}^{k}', commutative=False)

    def extractTasks(self, node):

        tName = NameGenerator('v')
        tasks = {}

        def getTasks(node):
            if node.func in [sy.Add, sy.Mul]:
                name = tName.get()
                # Get operation and dependencies
                if node.func == sy.Add:
                    op = '+'
                elif node.func == sy.Mul:
                    op = 'o'
                dep = [getTasks(n) for n in node.args]
                # Some fix to merge the -1 into one given tasks
                if isinstance(dep[0], sy.core.numbers.NegativeOne):
                    merged = dep[0] * dep[1]
                    dep = [merged] + dep[2:]
                # Store task in dictionary
                tasks[name] = {'op': op, 'dep': dep}
            else:
                name = node
            return name

        getTasks(node)

        return tasks

    def buildNextNode(self, n, k):
        newSol = null
        for op in self.blockOperators:
            nMod, kMod = op['dep']
            newSol += op['sym'] * self.node(n + 1 + nMod, k + 1 + kMod)
        newSol.simplify()
        self.dico[n + 1, k + 1] = newSol

    def taskToGraph(self, tasks, n, k):
        for key, value in tasks.items():
            if key.split('_')[-1] == '0':
                val = f'u_{n}^{k}'
            else:
                val = key + f'_{n}^{k}'
            dep = []
            oper = 'C'
            for item in value['dep']:
                if not isinstance(item, sy.Symbol):
                    if isinstance(item, sy.Expr):
                        if g not in item.free_symbols and f not in item.free_symbols:
                            dep.append(item)
                        else:
                            if g in item.free_symbols:
                                oper = 'G'
                            else:
                                oper = 'F'
                    else:
                        if isinstance(item, str):
                            if item.startswith('v'):
                                tmp_task = item + f'_{n}^{k}'
                                dep.append(tmp_task)
                        else:
                            dep.append(item)
                else:
                    if g not in item.free_symbols and f not in item.free_symbols:
                        dep.append(item)
                    else:
                        if g in item.free_symbols:
                            oper = 'G'
                        else:
                            oper = 'F'

            if val.startswith('v'):
                if val.split('_')[1] == '1':
                    pos = (n-.4, k)
                elif val.split('_')[1] == '2':
                    pos = (n-.4, k+.5)
                elif val.split('_')[1] == '3':
                    pos = (n, k)
            else:
                pos = (n, k+.5)
            self.add_node(op=oper,
                          predecessors=dep,
                          set_values=[val],
                          cost=1,
                          point=n,
                          pos=pos)

    def build_graph(self):
        for k in range(max(self.iterations)):
            for n in range(self.nt):
                if k <= self.iterations[n]:
                    self.taskToGraph(self.extractTasks(self.dico[n, k]), n, k)

    def boundary_condition(self):
        self.dico[0, 0] = self.node(0, 0)
        for n in range(self.nt):
            self.dico[n + 1, 0] = g * self.node(n, 0)

        for k in range(max(self.iterations)):
            for n in range(self.nt):
                if k <= self.iterations[n]:
                    self.buildNextNode(n, k)

        self.add_node(op='C',
                      predecessors=['u_0'],
                      set_values=['u_0^0'],
                      cost=0,
                      point=0,
                      pos=(0, .5))

    def compute(self):
        self.boundary_condition()
        self.build_graph()
        if self.sim_graph:
            self.simplify_graph()


parareal_model = SympyBasedApproach(cost_fine=4, cost_coarse=1, nt=4, iters=[0, 1, 2, 3], conv_crit=1, simplify_graph=False)
parareal_model.compute()
parareal_model.plot_dag()

parareal_model = SympyBasedApproach(cost_fine=4, cost_coarse=1, nt=4, iters=[0, 1, 2, 3], conv_crit=1, simplify_graph=True)
parareal_model.compute()
parareal_model.plot_dag()

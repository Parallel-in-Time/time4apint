from PintGraph import PintGraph


class GraphBasedApproach(PintGraph):
    def __init__(self, cost_fine: float, cost_coarse: float, cost_copy: float = 0, cost_correction: float = 0,
                 simplify_graph=True, *args: object, **kwargs: object) -> None:
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

    def block_node_simple(self, k, n):
        if k >= self.iterations[n]:
            pred_k = self.iterations[n]
            pred_k_plus_1 = self.iterations[n]
        else:
            pred_k = k
            pred_k_plus_1 = k + 1
        self.add_node(op=f"F",
                      predecessors=[f'u_{pred_k}_{n}'],
                      set_values=[f'v_1_{k}_{n + 1}_1'],
                      cost=self.cost_fine,
                      point=n + 1,
                      pos=(n + 1 - .3, k + 1), )
        self.add_node(op=f"G",
                      predecessors=[f'u_{pred_k}_{n}'],
                      set_values=[f'v_1_{k}_{n + 1}_2'],
                      cost=self.cost_coarse,
                      point=n + 1,
                      pos=(n + 1 + .3, k + 1))
        self.add_node(op=f"G",
                      predecessors=[f'u_{pred_k_plus_1}_{n}'],
                      set_values=[f'v_2_{k + 1}_{n + 1}'],
                      cost=0,
                      point=n + 1,
                      pos=(n + 1 - .3, k + 1 + .5))
        self.add_node(op="+",
                      predecessors=[f'v_1_{k}_{n + 1}_1', f'v_1_{k}_{n + 1}_2', f'v_2_{k + 1}_{n + 1}'],
                      set_values=[f'u_{k + 1}_{n + 1}'],
                      cost=0,
                      point=n + 1,
                      pos=(n + 1 + .3, k + 1 + .5))

    def build_graph(self):
        for k in range(max(self.iterations)):
            for n in range(self.nt - 1):
                if k <= self.iterations[n]:
                    print(k, n)
                    self.block_node_simple(k=k, n=n)

    def boundary_condition(self):
        self.add_node(op="init_cond",
                      predecessors=['u_0'],
                      set_values=['u_0_0'],
                      cost=0,
                      point=0,
                      pos=(0, 0))
        for n in range(self.nt - 1):
            self.add_node(op='G',
                          predecessors=[f'u_0_{n}'],
                          set_values=[f'u_0_{n + 1}'],
                          cost=self.cost_coarse,
                          point=n + 1,
                          pos=(n + 1, 0))

    def compute(self):
        self.boundary_condition()
        self.build_graph()
        if self.sim_graph:
            self.simplify_graph()


parareal_model = GraphBasedApproach(cost_fine=4, cost_coarse=1, nt=4, iters=[0, 1, 2], conv_crit=1, simplify_graph=False)
parareal_model.compute()
parareal_model.plot_dag()

parareal_model = GraphBasedApproach(cost_fine=4, cost_coarse=1, nt=4, iters=[0, 1, 2], conv_crit=1, simplify_graph=True)
parareal_model.compute()
parareal_model.plot_dag()


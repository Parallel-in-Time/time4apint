from typing import Any

from dynamic_site.app import App, ResponseStages
from dynamic_site.stage import parameters as par
import dynamic_site.stage.stages as stages

from blockops import BlockOperator, BlockIteration, I

# ===================
# Documentation Stage
# ===================

s1_docs = stages.DocsStage(
    "Quick Documentation",
    r"""
Consider the Parareal block update formula :

$$
u^{k+1}_{n+1} = F(u^{k}_n) + G(u^{k+1}_n) - G(u^{k}_n)
$$

Define the number of blocks $N$ (time-intervals), the number of iterations $K$ 
(eventually different for each block), and the cost of $F$
and $G$.
Then choose a scheduler type :

- BLOCK-BY-BLOCK : uses $N$ processors, where each processor is dedicated
to one time block
- LOWEST-COST-FIRST : uses $N$ processors, and compute first the tasks
with lower cost
- OPTIMAL : eventually use more than $N$ processors to minimize the
overall computation time 
""",
)

# ==============
# Settings Stage
# ==============

SCHEDULERS = ['LOWEST-COST-FIRST', 'OPTIMAL', 'BLOCK-BY-BLOCK']

pararealSettings = [
    par.StrictlyPositiveInteger(
        unique_id="nBlocks", name="$N$",
        placeholder="Number of Blocks",
        doc="Strictly positive integer",
        optional=False,
    ),
    par.FloatList(
        unique_id="nIter", name="$K$",
        placeholder="Number of Iterations",
        doc="Number of iteration for each block (1 or N values)",
        optional=False,
    ),
    par.Float(
        unique_id='costF', name='Computation time for $F$', 
        placeholder='Floating point number', 
        doc='Computation time for the fine solver', 
        optional=False
    ),
    par.Float(
        unique_id='costG', name='Computation time for $G$', 
        placeholder='Floating point number', 
        doc='Computation time for the coarse solver', 
        optional=False
    ),
    par.Enumeration(
        unique_id='schedulerType', name='Scheduler Type', 
        placeholder='', 
        doc='Type of scheduler use for Parareal', 
        optional=False,
        choices=SCHEDULERS,
        value='BLOCK-BY-BLOCK'
    ),
]

s1_settings = stages.SettingsStage(
    "pararealSettings", "Parareal Settings", pararealSettings, False
)


# ===========
# Plots Stage
# ===========

s1_plot = stages.PlotsStage("Parareal Schedule", None)

# ====================================================
#                  Accuracy App
# ====================================================
class PararealSchedule(App):
    def __init__(self) -> None:
        super().__init__(title="Parareal Schedule")

    def compute(self, response_data: dict[str, Any] | None) -> ResponseStages:
        
        # Create a response, where stages will be added to
        r = ResponseStages()

        # Initial request
        r.add_docs_stage(s1_docs)
        if not response_data:
            r.add_settings_stage(s1_settings)
            r.add_plot_stage(s1_plot)
            return r

        # Convert parameters to correct types
        pararealSettings = s1_settings.convert_to_types(
            response_data["pararealSettings"]
        )
        # Add the settings with the set values
        r.add_settings_stage(
            s1_settings.copy_from_response(response_data["pararealSettings"])
        )
        
        G = BlockOperator('G', cost=pararealSettings['costG'])
        F = BlockOperator('F', cost=pararealSettings['costF'])
        N = pararealSettings['nBlocks']
        K = [int(k) for k in pararealSettings['nIter']]
        K = K[0] if len(K) == 1 else K
        
        schedulerType = pararealSettings['schedulerType']

        parareal = BlockIteration(
            "(F - G) u_{n}^k + G * u_{n}^{k+1}",
            propagator="F", predictor="G", F=F, G=G, I=I, name='Parareal')

        fig = parareal.plotSchedule(N, K, nProc=N, schedulerType=schedulerType)
        
        # === Response ===
    
        plot_stage = s1_plot.copy()
        plot_stage.plot = fig.to_json()
        r.add_plot_stage(plot_stage)
        
        return r

        

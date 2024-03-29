from typing import Any

from wepps.app import App, ResponseStages
from wepps.stage import parameters as par
import wepps.stage.stages as stages

from blockops import BlockOperator, BlockIteration

# ===================
# Documentation Stage
# ===================

s1_docs = stages.DocsStage(
    "Quick Documentation",
    r"""
Consider the block update formula of Parareal with overlap 
(MGRIT with FCF relaxation) :

$$
u^{k+1}_{n+1} = F^2 (u^{k}_{n-1}) + G(u^{k+1}_n) - G \circ F(u^{k}_{n-1})
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

s1_plot = stages.PlotsStage("Parareal FCF Schedule")

CAPTION_FORMAT = """
**Performance Estimation ($N_p={nProcs}$):**

- Runtime : {time:.1f}
- Speedup : {speedup:.1f}
- Efficiency : {efficiency:.1f}%
"""

# ====================================================
#                  Accuracy App
# ====================================================
class PararealSchedule(App):
    def __init__(self) -> None:
        super().__init__(title="Parareal FCF Schedule")

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

        pararealFCF = BlockIteration(
            "(F - G)*F u_{n-1}^k + G u_{n}^{k+1}",
            propagator="F", predictor="G", F=F, G=G, name='PararealFCF')

        fig = pararealFCF.plotSchedule(N, K, nProc=N, schedulerType=schedulerType)
        time = pararealFCF.getRuntime(N, K, N, schedulerType)
        speedup, efficiency, nProcs, _ = pararealFCF.getPerformances(
            N, K, N, schedulerType)
        
        # === Response ===
    
        plot_stage = s1_plot.copy()
        plot_stage.caption = CAPTION_FORMAT.format(
            time=time, N=N, speedup=speedup, efficiency=efficiency*100,
            nProcs=nProcs)
        plot_stage.plot = fig.to_json()
        r.add_plot_stage(plot_stage)
        
        return r

        

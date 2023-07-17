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
Incoming ...
""",
)

# ==============
# Settings Stage
# ==============

SCHEDULERS = ['LOWEST-COST-FIRST', 'OPTIMAL', 'BLOCK-BY-BLOCK']

pararealSettings = [
    par.StrictlyPositiveInteger(
        "nBlocks",
        r"$N$",
        r"Number of Blocks",
        r"Strictly positive integer",
        False,
    ),
    par.StrictlyPositiveInteger(
        "nIter",
        r"$K$",
        r"Number of Iterations",
        r"Strictly positive integer",
        False,
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
        K = pararealSettings['nIter']
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

        

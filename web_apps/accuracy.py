from typing import Any

import numpy as np
import plotly.graph_objects as go

import dynamic_site.stage.stages as stages
from blockops import BlockIteration, BlockOperator
from blockops.problem import BlockProblem
from blockops.run import PintRun
from blockops.scheduler import getSchedule
from blockops.taskPool import TaskPool
from blockops.webutils import convert_to_web
from dynamic_site.app import App, ResponseStages
from dynamic_site.stage import parameters

# ===================
# Documentation Stage
# ===================

d1_docs = stages.DocsStage(
    "Definition of a Block Problem",
    r"""
A block problem is a problem.
(Maybe a more detailed description here or an injected `BlockIteration.__doc__`)

- $N$ : Number of blocks for the global problem.
- $K$ : Number of iterations per block.
""",
)

# ==============
# Settings Stage
# ==============

# block_problem_web_params = convert_to_web(BlockProblem.PARAMS)
block_problem_web_params = [
    parameters.StrictlyPositiveInteger(
        "N",
        r"$N$",
        r"Number of blocks",
        r"Strictly positive integer",
        False,
    ),
    parameters.StrictlyPositiveInteger(
        "K",
        r"$K$",
        r"Number of iterations per block",
        r"Strictly positive integer",
        False,
    ),
]

s1_settings = stages.SettingsStage(
    "block_problem", "Definition of a block problem", block_problem_web_params, False
)


# ===========
# Plots Stage
# ===========

p1_plot = stages.PlotsStage("Schedule", None)

# ====================================================
#                  Accuracy App
# ====================================================


class Accuracy(App):
    def __init__(self) -> None:
        super().__init__(title="Accuracy")

    def compute(self, response_data: dict[str, Any] | None) -> ResponseStages:
        # Create a response, where stages will be added to
        r = ResponseStages()

        # Initial request
        if not response_data:
            r.add_docs_stage(d1_docs)
            r.add_settings_stage(s1_settings)
            r.add_plot_stage(p1_plot)
            return r

        # =================
        # Some computations

        # id of the settings stage, then variable
        nBlocks = int(response_data["block_problem"]["N"])
        K = [int(response_data["block_problem"]["K"])] * nBlocks

        G = BlockOperator("G", cost=1)
        F = BlockOperator("F", cost=10)

        parareal = BlockIteration(
            "(F - G) u_{n}^k + G u_{n}^{k+1}",
            propagator="F",
            predictor="G",
            F=F,
            G=G,
            name="Parareal",
        )

        pspeedup, efficiency, nProc = parareal.getPerformances(
            N=nBlocks, K=K, nProc=nBlocks + 1, verbose=True
        )

        # Change docs and add information
        docs_d1 = d1_docs.copy()
        docs_d1.text += (
            f"\n\npspeedup: {pspeedup}\nefficiency: {efficiency}\nProc: {nProc}\n"
        )

        r.add_docs_stage(d1_docs)

        # Add the settings with the set values
        r.add_settings_stage(
            s1_settings.copy_from_response(response_data["block_problem"])
        )

        # Build the plot
        # parareal.plotSchedule(
        N = nBlocks
        nProc = nBlocks
        schedule_type = "BLOCK-BY-BLOCK"
        K = parareal.checkK(N=N, K=K)
        run = PintRun(blockIteration=parareal, nBlocks=N, kMax=K)
        pool = TaskPool(run=run)
        s = getSchedule(
            taskPool=pool, nProc=nProc, nPoints=N + 1, schedulerType=schedule_type
        )

        fig = go.Figure(
            data=[],
            layout=go.Layout(
                titlefont_size=16,
                showlegend=True,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
            ),
        )
        colors = {}
        for key, value in s.schedule.items():
            if value.color not in colors:
                colors[value.color] = [[], [], value.name, value.end - value.start]
        for key, value in s.schedule.items():
            time = value.end - value.start
            if time > 0:
                shapes_x = colors[value.color][0]
                shapes_y = colors[value.color][1]
                shapes_x.append(value.start)
                shapes_x.append(value.start + time)
                shapes_x.append(value.start + time)
                shapes_x.append(value.start)
                shapes_x.append(value.start)
                shapes_x.append(None)
                shapes_y.append(value.proc + 0.225)
                shapes_y.append(value.proc + 0.225)
                shapes_y.append(value.proc + 0.725)
                shapes_y.append(value.proc + 0.725)
                shapes_y.append(value.proc + 0.225)
                shapes_y.append(None)

        for key, value in colors.items():
            fig.add_trace(
                go.Scatter(
                    x=value[0],
                    y=value[1],
                    fill="toself",
                    fillcolor=key,
                    marker=dict(color=key, size=1, line=dict(color=key, width=0.1)),
                    hoverinfo="text",
                    text="Cost:" + str(value[3]),
                    name=value[2],
                    showlegend=True,
                )
            )
        fig.update_xaxes(title="Time")
        fig.update_yaxes(title="Processor rank")
        fig.update_yaxes(
            ticktext=["P" + str(i) for i in range(s.nProc - 1, -1, -1)],
            tickvals=(np.linspace(s.nProc - 1, 0, s.nProc) + 0.5).tolist(),
        )
        plot_stage = p1_plot.copy()
        plot_stage.plot = fig.to_json()

        r.add_plot_stage(plot_stage)

        return r

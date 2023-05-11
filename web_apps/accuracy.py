import copy
from typing import Any

import plotly.graph_objects as go

import dynamic_site.stage.stages as stages
from blockops.problem import BlockProblem
from blockops.webutils import convert_to_web
from dynamic_site.app import App, StagesMessage
from dynamic_site.stage.parameters import (Float, FloatList,
                                           StrictlyPositiveInteger)

# ===================
# Documentation Stage
# ===================

d1_docs = stages.DocsStage(
    'D1', 'Definition of a Block Problem', r'''
- $\lambda$ : the value(s) for $\lambda$
- $T$ : Total simulation time 
- $N$ : number of blocks for the global problem
- $u_0$ : the initial solution (default=1)
- scheme : the chosen BlockScheme for fine level

A test equation
$$
a = 5^n.
$$
''', False, None)

# ==============
# Settings Stage
# ==============

block_problem_web_params = convert_to_web(BlockProblem.PARAMS)
s1_settings = stages.SettingsStage('S1', 'Definition of a Block Problem',
                                   block_problem_web_params, False, None)

scheme_param = copy.deepcopy(BlockProblem.PARAMS['scheme'])
scheme_param.uniqueID = 'BlockProblem_scheme_s2'
scheme_params = convert_to_web({'scheme': scheme_param})
print(scheme_params[0].id)
s2_settings = stages.SettingsStage('S2', 'Definition of a Block Scheme',
                                   scheme_params, False, 'S1')

# ===========
# Plots Stage
# ===========

p1_params = [
    FloatList('p1-err', r'`\lambda` error', 'Lambda error values',
              '2D array containing error value for each lambda values.', None),
    FloatList(
        'p1-stab', r'`\lambda` stab', 'Lambda amplification factor',
        '2D array containing amplification factor for each lambda values.',
        [0.0, 1.0]),
    StrictlyPositiveInteger(
        'p1-nvals', r'`n_\lambda`', 'Number of lambda values',
        'Number of lambda values to display in each direction of the complex plane',
        500),
    FloatList('p1-relambounds', r'`\mathfrak{Re}(\lambda)` bounds',
              'Real lambda bounds', 'Bounds for the real lambda values.',
              [-4., 0.5]),
    FloatList('p1-imlambounds', r'`\mathfrak{Im}(\lambda)` bounds',
              'Imaginary lambda bounds',
              'Bounds for the imaginary lambda values.', [-3., 3.]),
    Float('p1-emin', r'`e_\{\min\}`', 'Min error exponent',
          'Minimum error exponent for the contour plot.', -7.0),
    Float('p1-emax', r'`e_\{\max\}`', 'Max error exponent',
          'Maximum error exponent for the contour plot.', 0.0),
]

p1_plots = stages.PlotsStage('P1', 'Error', p1_params, None, False, None)


def dummy_fig_1():
    fig = go.Figure(data=go.Contour(
        z=[[10, 10.625, 12.5, 15.625, 20], [5.625, 6.25, 8.125, 11.25, 15.625],
           [2.5, 3.125, 5., 8.125, 12.5], [0.625, 1.25, 3.125, 6.25, 10.625],
           [0, 0.625, 2.5, 5.625, 10]], ))
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    return fig.to_json()


# ====================================================
#                  Accuracy App
# ====================================================


class Accuracy(App):

    def __init__(self) -> None:
        super().__init__(title='Accuracy')

    def compute(self, response_data: dict[str, Any] | None) -> StagesMessage:
        if not response_data:
            return StagesMessage([d1_docs], [s1_settings, s2_settings], [
                p1_plots,
            ])

        # if f'{scheme_param.uniqueID}s2' in response_data:
        #     print('yep')
        docs_d1 = d1_docs

        settings_s1 = s1_settings.copy_from_response(response_data)
        settings_s1.activated = True
        settings_s2 = s2_settings

        plot_p1 = p1_plots.copy_from_response(response_data)
        plot_p1.plot = dummy_fig_1()

        return StagesMessage([docs_d1], [settings_s1, settings_s2], [plot_p1])

from typing import Any

from dynamic_site.app import App, StagesMessage
import dynamic_site.stage.stages as stages
from dynamic_site.stage.parameters import (Integer, PositiveInteger,
                                           StrictlyPositiveInteger,
                                           PositiveFloat, Float, Enumeration,
                                           FloatList, Boolean)

import plotly.graph_objects as go

# ===================
# Documentation Stage
# ===================

d1_docs_text = r'''
Test equation with a $\phi \in \mathbb{R}$
$$
\begin{align*}
x^2 + y^2 &= 1 \\\\
y &= \sqrt{1 - x^2}.
\end{align*}
$$
'''

d1_docs = stages.DocsStage('D1', 'The first documentation stage', d1_docs_text,
                           False, None)

d2_docs = stages.DocsStage(
    'D2', '2nd docs stage', r'''
This stage depends on the first.


$$
\alpha + \frac{2\beta}{\gamma}
$$
''', False, 'D1')

# ==============
# Settings Stage
# ==============

s1_params = [
    Integer('s1-Integer', r'`i`', r'Placeholder no latex: `\alpha`',
            r'Hover docs (no latex: `\phi`)'),
    PositiveInteger('s1-PositiveInteger', r'`\xi`',
                    'Placeholder: for PositiveInteger', r'Hover docs'),
    StrictlyPositiveInteger('s1-StrictlyPositiveInteger', r'`\phi`',
                            'Placeholder: for StrictlyPositiveInteger',
                            r'Hover docs'),
    PositiveFloat('s1-PositiveFloat', r'`\alpha_{\beta - 2}^3`',
                  'Placeholder: for PositiveFloat', r'Hover docs'),
    Float('s1-Float', r'`\rho`', 'Placeholder: for Float', r'Hover docs'),
    Enumeration('s1-Enumeration', 'Selection', 'Placeholder: for Enumeration',
                r'Hover docs', ['First', 'Second', 'Third']),
    FloatList('s1-FloatList', r'`n`', r'Placeholder: for FloatList',
              r'Hover docs'),
    Boolean('s1-Boolean', r'`\mathbb{B}`', 'Placeholder: for Boolean',
            r'Hover docs')
]

s1_settings = stages.SettingsStage('S1', 'Definition of a Block Problem',
                                   s1_params, False, None)

# ===========
# Plots Stage
# ===========

p1_params = [
    FloatList('p1-FloatList', r'`\lambda` error', 'Lambda error values',
              '2D array containing error value for each lambda values.', None)
]

p1_plots = stages.PlotsStage('P1', 'Contour', p1_params, None, False, None)

p2_params = [
    Float('p2-float', r'`\min`', 'Minimum', 'Minimum of something.', -7.0),
]
p2_plots = stages.PlotsStage('P2', 'Plot 2', p2_params, None, False, 'S1')

# =============
# Dummy figures
# =============


def dummy_fig_1():
    fig = go.Figure(data=go.Contour(
        z=[[10, 10.625, 12.5, 15.625, 20], [5.625, 6.25, 8.125, 11.25, 15.625],
           [2.5, 3.125, 5., 8.125, 12.5], [0.625, 1.25, 3.125, 6.25, 10.625],
           [0, 0.625, 2.5, 5.625, 10]], ))
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    return fig.to_json()


# ====================================================
#                     Demo App
# ====================================================


class Demo(App):

    def __init__(self) -> None:
        super().__init__(title='API Demonstration')

    def compute(self, response_data: dict[str, Any] | None) -> StagesMessage:
        # If response_data is empty ({}), then its the initial request
        if not response_data:
            return StagesMessage([d1_docs, d2_docs], [s1_settings],
                                 [p1_plots, p2_plots])

        # Otherwise, there is data, so show it in the docs
        docs_d1 = d1_docs.copy()
        for s1_param in [
                's1-Integer', 's1-PositiveInteger',
                's1-StrictlyPositiveInteger', 's1-PositiveFloat', 's1-Float',
                's1-Enumeration', 's1-FloatList', 's1-Boolean'
        ]:
            docs_d1.text += f'- {s1_param}: {response_data[s1_param]}\n'
        docs_d2 = d2_docs

        # Create a copy with the values from the response, so that there is no global change of the data for another request
        settings_s1 = s1_settings.copy_from_response(response_data)
        # Activate it, so that the dependencies will be shown
        settings_s1.activated = True
        # We can also change parameter values
        settings_s1.parameters[0].default = 5

        # Copy the response too so that the parameter values will be saved
        plot_p1 = p1_plots.copy_from_response(response_data)
        # Set the figure data
        plot_p1.plot = dummy_fig_1()

        # No copy, so the parameter values will be reset
        plot_p2 = p2_plots
        plot_p2.plot = dummy_fig_1()

        # Then return the stages
        return StagesMessage([docs_d1, docs_d2], [settings_s1],
                             [plot_p1, plot_p2])

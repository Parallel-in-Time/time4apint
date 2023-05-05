import dynamic_site.stage.stages as stages
import dynamic_site.stage.utils as utils
from blockops.problem import BlockProblem
from blockops.webutils import convert_to_web
from dynamic_site.stage.parameters import Float, FloatList, StrictlyPositiveInteger

# ===================
# Documentation Stage
# ===================

d1_docs = stages.DocsStage(
    'D1', 'Definition of a Block Problem', r'''
- lam : the value(s) for $\lambda$
- tEnd : total simulation time $T$
- nBlocks : number of blocks $N$ for the global problem
- u0 : the initial solution $u_0$ (default=1)
- scheme : the chosen BlockScheme for fine level

A test equation
$$
a = 5^n.
$$
''', False, None)

d2_docs = stages.DocsStage('D2', 'Very informative docs', r'''
$$
\alpha + \frac{2\beta}{\gamma}
$$
''', False, 'D1')

# ==============
# Settings Stage
# ==============

block_problem_web_params = convert_to_web(BlockProblem.PARAMS)
s1_settings = stages.SettingsStage('S1', 'Definition of a Block Problem',
                                   block_problem_web_params, 'Compute', False,
                                   None)

s2_params = [
    StrictlyPositiveInteger('s2-nu', r'`\nu_\lambda`', 'Something',
                            'Very informative text.', 3),
    Float('s2-gamma', r'`\gamma`', 'Something else', 'Much more informative.',
          51.3),
    Float('s2-epsilon', r'`\varepsilon`', 'A parameter', 'This is an epsilon.',
          4.0),
]

s2_settings = stages.SettingsStage('S2', 'Another Stage', s2_params, 'Compute',
                                   False, 'S1')

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

p2_params = [
    FloatList('p2-niter', r'`n` iteration', 'Lambda error values',
              '2D array containing error value for each lambda values.',
              [1.0]),
    StrictlyPositiveInteger(
        'p2-nvals', r'`n_\lambda`', 'Number of lambda values',
        'Number of lambda values to display in each direction of the complex plane',
        500),
    Float('p2-emin', r'`e_\{\min\}`', 'Min error exponent',
          'Minimum error exponent for the contour plot.', -7.0),
    Float('p2-emax', r'`e_\{\max\}`', 'Max error exponent',
          'Maximum error exponent for the contour plot.', 0.0),
]
p2_plots = stages.PlotsStage('P2', 'Iteration', p2_params, None, False, 'S1')

# =============
# Dummy figures
# =============

import plotly.graph_objects as go


def dummy_fig_1():
    fig = go.Figure(data=go.Contour(
        z=[[10, 10.625, 12.5, 15.625, 20], [5.625, 6.25, 8.125, 11.25, 15.625],
           [2.5, 3.125, 5., 8.125, 12.5], [0.625, 1.25, 3.125, 6.25, 10.625],
           [0, 0.625, 2.5, 5.625, 10]], ))
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    return fig.to_json()


def dummy_fig_2():
    fig = go.Figure(data=go.Contour(
        z=[[10, 10.625, 12.5, 15.625, 20], [5.625, 6.25, 8.125, 11.25, 15.625],
           [2.5, 3.125, 5., 8.125, 12.5], [0.625, 1.25, 3.125, 6.25, 10.625],
           [0, 0.625, 2.5, 5.625, 10]],
        x=[-9, -6, -5, -3, -1],
        y=[0, 1, 4, 5, 7]))
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), autosize=True)
    return fig.to_json()
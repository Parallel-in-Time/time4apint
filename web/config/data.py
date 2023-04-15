import web.stage.stages as stages
import web.stage.utils as utils
from blockops.problem import BlockProblem
from blockops.webutils import convert_to_web

# ===================
# Documentation Stage
# ===================

d1_text = utils.render_md(r'''
- lam : the value(s) for `\lambda`
- tEnd : total simulation time `T`
- nBlocks : number of blocks `N` for the global problem
- u0 : the initial solution `u_0` (default=1)
- scheme : the chosen BlockScheme for fine level

A test equation
$$
a = 5^n.
$$
''')

stage_1_docs = stages.DocsStage('D1', 'Definition of a Block Problem', d1_text,
                                None)

# ==============
# Settings Stage
# ==============

block_problem_web_params = convert_to_web(BlockProblem.PARAMS)
stage_1_block_problem = stages.SettingsStage('S1',
                                             'Definition of a Block Problem',
                                             block_problem_web_params,
                                             'Compute', None)

# ===========
# Plots Stage
# ===========

from web.stage.parameters import FloatList, StrictlyPositiveInteger, Float

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

stage_1_plots = stages.PlotsStage('P1', 'Error', p1_params, None, None)

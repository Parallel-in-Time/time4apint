from blockops.problem import BlockProblem

import web.utils as utils
import web.stages as stages

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

stage_1_block_problem = stages.SettingsStage('S1',
                                             'Definition of a Block Problem',
                                             BlockProblem.PARAMS, 'Compute',
                                             None)
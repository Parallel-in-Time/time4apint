import web.stage.stages as stages
import web.stage.utils as utils
from blockops.problem import BlockProblem

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

stage_1_block_problem = stages.SettingsStage('S1',
                                             'Definition of a Block Problem',
                                             BlockProblem.PARAMS, 'Compute',
                                             None)

# ===========
# Plots Stage
# ===========


def p1_params():
    from blockops.utils.params import (ParamClass, PositiveInteger,
                                       ScalarNumber, VectorNumbers, setParams)

    @setParams(
        err=VectorNumbers(),
        stab=VectorNumbers(),
        nVals=PositiveInteger(),
        reLamBounds=VectorNumbers(),
        imLamBounds=VectorNumbers(),
        eMin=ScalarNumber(),
        eMax=ScalarNumber(),
    )
    class P1Dummy(ParamClass):
        '''Docs

    Parameters
    ----------
    err : float, complex or np.1darray
        Lambda values.
    stab : float
        End of simulation interval :math:`T`.
    nVals : int
        Number of blocks :math:`N`.
    reLamBounds : str
        Time discretization scheme used for the block operators.
    imLamBounds : scalar, optional
        The initial solution :math:`u_0`. The default is 1.
    eMin : scalar
        min
    eMax : scalar
        max
        '''

        def __init__(self,
                     err,
                     stab,
                     nVals=500,
                     reLamBounds=[-4., 0.5],
                     imLamBounds=[-3., 3.],
                     eMin=-7.,
                     eMax=0.):
            # Initialize parameters
            self.initialize(locals())

    import copy
    return copy.deepcopy(P1Dummy.PARAMS)


stage_1_plots = stages.PlotsStage('P1', 'Error', p1_params(), None, None)

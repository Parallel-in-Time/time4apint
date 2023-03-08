from .documentation import Documentation

# --- Schemes ---
rk_type_params = {
    'defaults': {
        'points': 'EQUID',
        'quadType': 'RADAU-RIGHT',
        'form': 'N2N',
    },
    'nStepsPerPoint': {
        'default': 1,
        'type': 'int'
    },
}

collocation_type_params = {
    'defaults': {
        'points': 'LEGENDRE',
        'quadType': 'RADAU-RIGHT',
        'form': 'Z2N',
    },
    'quadProlong': {
        'default': False,
        'type': 'bool'
    },
}

schemes = {
    'BE': rk_type_params,
    'FE': rk_type_params,
    'TRAP': rk_type_params,
    'RK2': rk_type_params,
    'RK4': rk_type_params,
    'EXACT': rk_type_params,
    'COLLOCATION': collocation_type_params,
}

# --- Algorithms ---
algorithms = {
    'Parareal': [
        'scheme-approx-form',
    ],
    'ABGS': [
        'scheme-approx-form',
    ],
    'ABJ': [
        'scheme-approx-form',
    ],
    'TMG': [
        'MCoarse',
    ],
    'TMG-C': ['MCoarse', 'scheme-approx-form'],
    'TMG-F': ['MCoarse', 'scheme-approx-form'],
    'PFASST': ['MCoarse', 'scheme-approx-form'],
    'MGRIT-FCF': [
        'scheme-approx-form',
    ],
}

# --- Documentation ---
# Math equations in backticks: `a = b`
# r'' to insert \ if needed

docs = Documentation()

docs.add('N', r'`N`: Number of blocks `N`, strictly positive integer.')
docs.add('tEnd', r'`T`: Total simulation time `T`, strictly positive float. For generic analysis, current default is `T=N`.')
docs.add('scheme', r'**Scheme**: Time discretization scheme to use.')
docs.add('M', r'`M`: Number of time-points per blocks `M`, strictly positive integer.')
docs.add('points', r'''**Points**: Time point distribution for each block, can be either a list of points in `[0,1]` (ignore `M`) or a string in:
- EQUID: Equidistant point uniformly distributed on the block.
- LEGENDRE: Points distribution from Legendre polynomials.
- CHEBY-`\{i\}`: Points distribution from Chebychev polynomials of the `i`'th kind (`i \in \{1,2,3,4\}`).
''')
docs.add('quadType', r'''**QuadType**: quadrature type for each block, a string in:
- GAUSS: don't include left and right block boundary in the points. For `\text{points}=\text{LEGENDRE}` and `\text{points}=\text{CHEBY-}\{i\}`, correspond to the standard Gauss nodes with those distributions. For `\text{points}=\text{EQUID}`, uniformly distribute the points inside `(0,1)`.
- LOBATTO: include left and right block boundary points
- RADAU: `\{ \text{LEFT},\text{RIGHT}}`: include either the left or right block boundary point (only).''')
docs.add('form', r'''**Form**: Node formulation (generalized from collocation methods). This produce equivalent block operators, just written differently. It can be chosen from two values:
- Z2N: zeros-to-nodes formulation, _i.e_ the `\chi` operator produces a vector of the form `[u_0, u_0, ..., u_0]` and `\phi` represents the integration from `u_{0}` to each block time points.
- N2N: node-to-node formulation, _i.e_ the `\phi` operator produces a vector of the form `[u_0, 0, ..., 0]` and `\phi` represents the integration from one node to the next one.''')
docs.add('algorithm', r'**Algorithm**: Selected PinT algorithm.')
docs.add('schemeApproxPoints', r'**Scheme Approximation Points**: Defines the points of an approximate block operator.')
docs.add('schemeApproxForm', r'**Scheme Approximation Form**: Defines the form of an approximate block operator.')
docs.add('MCoarse', r'**MCoarse**: Define a coarse level using exactly the same discretization as the fine level, but with `\text{MCoarse} < M`.')

documentation = docs.get()

import mistune

class MathRenderer(mistune.HTMLRenderer):

    def codespan(self, text):
        return '`' + mistune.escape(text) + '`'


markdown = mistune.create_markdown(
            renderer=MathRenderer(),
            hard_wrap=True,
        )
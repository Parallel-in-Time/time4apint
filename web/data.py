import mistune

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
        'schemeApprox',
    ],
    'ABGS': [
        'schemeApprox',
    ],
    'ABJ': [
        'schemeApprox',
    ],
    'TMG': [
        'MCoarse',
    ],
    'TMG-C': ['MCoarse', 'schemeApprox'],
    'TMG-F': ['MCoarse', 'schemeApprox'],
    'PFASST': ['MCoarse', 'schemeApprox'],
    'MGRIT-FCF': [
        'schemeApprox',
    ],
}

# --- Documentation ---
# Math equations in backticks: `a = b`
# r'' to insert \ if needed
markdown_documentation = {
    'N':
    r'`N`: Number of blocks `N`, strictly positive integer.',
    'tEnd':
    r'`T`: Total simulation time `T`, strictly positive float. For generic analysis, current default is `T=N`.',
    'scheme':
    r'**Scheme**: Time discretization scheme to use.',
    'M':
    r'`M`: Number of time-points per blocks `M`, strictly positive integer.',
    'points':
    r'''**Points**: Time point distribution for each block, can be either a list of points in `[0,1]` (ignore `M`) or a string in:
- EQUID: Equidistant point uniformly distributed on the block.
- LEGENDRE: Points distribution from Legendre polynomials.
- CHEBY-`\{i\}`: Points distribution from Chebychev polynomials of the `i`'th kind (`i \in \{1,2,3,4\}`).
    ''',
    'quadType':
    r'''**QuadType**: quadrature type for each block, a string in:
- GAUSS: don't include left and right block boundary in the points. For `\text{points}=\text{LEGENDRE}` and `\text{points}=\text{CHEBY-}\{i\}`, correspond to the standard Gauss nodes with those distributions. For `\text{points}=\text{EQUID}`, uniformly distribute the points inside `(0,1)`.
- LOBATTO: include left and right block boundary points
- RADAU: `\{ \text{LEFT},\text{RIGHT}}`: include either the left or right block boundary point (only).''',
    'form':
    r'''**Form**: Node formulation (generalized from collocation methods). This produce equivalent block operators, just written differently. It can be chosen from two values:
- Z2N: zeros-to-nodes formulation, _i.e_ the `\chi` operator produces a vector of the form `[u_0, u_0, ..., u_0]` and `\phi` represents the integration from `u_{0}` to each block time points.
- N2N: node-to-node formulation, _i.e_ the `\phi` operator produces a vector of the form `[u_0, 0, ..., 0]` and `\phi` represents the integration from one node to the next one.''',
    'algorithm':
    r'**Algorithm**: Selected PinT algorithm.',
    'schemeApproxPoints':
    r'**Scheme Approximation Points**: Defines the points of an approximate block operator.',
    'schemeApproxForm':
    r'**Scheme Approximation Form**: Defines the form of an approximate block operator.',
    'MCoarse':
    r'**MCoarse**: Define a coarse level using exactly the same discretization as the fine level, but with `\text{MCoarse} < M`.',
}


# --- Utilities ---
class MathRenderer(mistune.HTMLRenderer):

    def codespan(self, text):
        return '`' + mistune.escape(text) + '`'


markdown = mistune.create_markdown(
    renderer=MathRenderer(),
    hard_wrap=True,
)

documentation = {
    key: markdown(md)
    for key, md in markdown_documentation.items()
}

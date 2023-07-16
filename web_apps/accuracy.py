from typing import Any
import numpy as np

from dynamic_site.app import App, ResponseStages
from dynamic_site.stage import parameters as par
import dynamic_site.stage.stages as stages

from blockops.schemes import BlockScheme, SCHEMES
from blockops.problem import BlockProblem 
from blockops.plots import Plotly as bp

# ===================
# Documentation Stage
# ===================

s1_docs = stages.DocsStage(
    "Defining the Block Problem",
    r"""
First define the **Block Problem** representing the time-dependant problem,
that can be represented into matrix form as :
    
$$
\begin{pmatrix}
    \phi & & &\\
    -\chi & \phi & &\\
    & \ddots & \ddots &\\
    & & -\chi & \phi
\end{pmatrix}
\begin{bmatrix}
    {\bf u}_1\\{\bf u}_2\\\vdots\\{\bf u}_N
\end{bmatrix}
=
\begin{bmatrix}
    \chi(u_0{\bf 1})\\0\\\vdots\\0
\end{bmatrix}
$$

with $N$ the number of blocks. Then the **Block Operators** $\phi$ and $\chi$
are determined considering the chosen time-integration method ... 
""",
)
    
s2_docs = stages.DocsStage(
    "Scheme-specific parameters",
    r"""
Define the Block Scheme parameters ...
""",
)

# ==============
# Settings Stage
# ==============

# block_problem_web_params = convert_to_web(BlockProblem.PARAMS)
block_problem_web_params = [
    par.StrictlyPositiveInteger(
        "nBlocks",
        r"$N$",
        r"Number of Blocks",
        r"Strictly positive integer",
        False,
    ),
    *[par.getParam(name, param) 
      for name, param in BlockScheme.PARAMS.items()
      if name in ['nPoints', 'ptsType', 'quadType']],
    par.Enumeration(
        'scheme', 
        'Scheme Type', 
        "Time-Integration in block", 
        "Time-Integration in block",
        optional=False,
        choices=list(SCHEMES.keys())),
]

s1_settings = stages.SettingsStage(
    "block_problem", s1_docs.title, block_problem_web_params, False
)


# ===========
# Plots Stage
# ===========

s1_plot = stages.PlotsStage("Error Contour", None)

# ====================================================
#                  Accuracy App
# ====================================================
STATUS = {'current': 's1'}

class Accuracy(App):
    def __init__(self) -> None:
        super().__init__(title="Accuracy on Complex Plane")

    def compute(self, response_data: dict[str, Any] | None) -> ResponseStages:
        # Create a response, where stages will be added to
        r = ResponseStages()

        # Initial request
        r.add_docs_stage(s1_docs)
        if not response_data:
            r.add_settings_stage(s1_settings)
            r.add_plot_stage(s1_plot)
            STATUS['current'] = 's1'
            return r


        # Convert parameters to correct types
        block_problem_data = s1_settings.convert_to_types(
            response_data["block_problem"]
        )

        # Then access the converted variables
        scheme = block_problem_data["scheme"]
        Scheme = SCHEMES[scheme]
        
        # Add scheme-specific parameters
        block_scheme_params = [
            par.getParam(name, param) 
            for name, param in Scheme.PARAMS.items()
            if name not in BlockScheme.PARAMS.keys()
        ]
        block_scheme_params += [ 
            par.Float(
                unique_id='zoom', 
                name='Zoom', 
                placeholder="Floating point number", 
                doc="Zoom factor for the plot", 
                optional=False, 
                value=1)]

        # Add the settings with the set values
        r.add_settings_stage(
            s1_settings.copy_from_response(response_data["block_problem"])
        )
        
        # Add scheme-specific settings
        s2_settings = stages.SettingsStage(
            "additional", 
            'Additional parameters', 
            block_scheme_params, 
            False
        )
        r.add_settings_stage(s2_settings)
        
        if STATUS['current'] == 's1':
            r.add_plot_stage(s1_plot)
            STATUS['current'] = 's2'
            return r
            
        if STATUS['current'] == 's2':
            
            parS1 = s1_settings.convert_to_types(
                response_data["block_problem"]
            )
            parS2 = s2_settings.convert_to_types(
                response_data["additional"]
            )
            zoom = parS2.pop('zoom')
            parS1.update(parS2)
            parS1['tEnd'] = parS1['nBlocks']
            
            
            reLam = np.linspace(-4*zoom, 0.5*zoom, 256)
            imLam = np.linspace(-3*zoom, 3*zoom, 256)
            
            lam = reLam[:, None] + 1j*imLam[None, :]
            prob = BlockProblem(lam.ravel(), **parS1)

            uExact = prob.getSolution('exact')
            uNum = prob.getSolution('fine')
            err = np.abs(uExact-uNum)

            stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
            errEnd = err[-1, :, -1].reshape(lam.shape) # For later ...
            errMax = np.max(err, axis=(0, -1)).reshape(lam.shape)

            err = errMax

            # Plot discretization error on complex plane
            fig = bp.plotAccuracyContour(reLam, imLam, err, stab)
            
            # === Response ===
        
            plot_stage = s1_plot.copy()
            plot_stage.plot = fig.to_json()
            r.add_plot_stage(plot_stage)
        
        return r

        

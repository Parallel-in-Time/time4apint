#!/usr/bin/env python3
import numpy as np
from flask import Flask, jsonify, render_template, request

from mpld3 import fig_to_dict

from blockops import BlockProblem

from web.utilities import discretization_error, pint_iter, pint_error

app = Flask(__name__,
            static_url_path='',
            static_folder='web/static',
            template_folder='web/templates')

# --- Schemes ---
rk_type_params = {
    'defaults': {
        'nodes': 'EQUID',
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
        'nodes': 'LEGENDRE',
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/app')
def application():
    return render_template('app.html')


@app.route('/app/data')
def app_data():
    return jsonify({'algorithms': algorithms, 'schemes': schemes})


@app.route('/compute-stage-1', methods=['POST'])
def compute_stage_1():
    # Fetch the selected values
    try:
        # TODO: Check for strictly positive etc.

        # Stage 1-A: Time block decomposition
        N = int(request.json['N'])
        tEnd = int(request.json['tEnd'])

        # Stage 1-B: base (fine) block propagator
        scheme = request.json['scheme']  # TODO: Check for string?
        if scheme not in schemes.keys():
            raise RuntimeError(
                f'scheme {scheme} unknown. Must be one of {schemes.keys()}')
        M = int(request.json['M'])

        # Optional parameters
        points = int(request.json['points'])
        quadType = int(request.json['quadType'])
        form = int(request.json['form'])
    except Exception as e:
        return jsonify({'error': f'[PARAM ERROR]\n{str(e)}'}), 500

    data = {}
    # Compute stuff here
    try:
        # TODO: Actually compute some stuff here
        data['delta_T'] = 0.2
        data['block_points_distribution'] = 15.2
        data['fine_discretization_error'] = 'I am a plot!'
        data['estimated_fine_block_cost'] = 8.3

    except Exception as e:
        return jsonify({'error': f'[COMPUTE ERROR]\n{str(e)}'}), 500

    return jsonify({'data': data})


@app.route('/compute-stage-2', methods=['POST'])
def compute_stage_2():
    # Fetch the selected values
    try:
        # TODO: Check for strictly positive etc.

        # Stage 2: Selection and analysis of a PinT algorithm
        algo = request.json['algo']
        schemeApprox = request.json['schemeApprox']
        MCoarse = int(request.json['MCoarse'])
        if algo not in algorithms.keys():
            raise RuntimeError(
                f'Algorithm {algo} unknown. Must be one of {algorithms.keys()}'
            )

        for param_dependency in algorithms[algo]:
            if request.json[param_depency] == None:
                raise RuntimeError(
                    f'Algorithm {algo} depends on the param {param_dependency} but is None.'
                )
    except Exception as e:
        return jsonify({'error': f'[PARAM ERROR]\n{str(e)}'}), 500

    data = {}
    # Compute stuff here
    try:
        # TODO: Actually compute some stuff here
        data['block_iteration'] = 7
        data['approximation_error'] = 'I am a plot!'
        data['coarse_error'] = 'I am a plot!'
        data['PinT_error'] = 'I am a plot!'
        data['PinT_iterations'] = 9
        data['PinT_speedup'] = 'I am a plot!'

    except Exception as e:
        return jsonify({'error': f'[COMPUTE ERROR]\n{str(e)}'}), 500

    return jsonify({'data': data})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

#!/usr/bin/env python3
import numpy as np
from flask import Flask, jsonify, render_template, request

import mistune

from mpld3 import fig_to_dict

from blockops import BlockProblem

from web.utilities import discretization_error, pint_iter, pint_error
# from web.data import algorithms, schemes
import web.data as data

app = Flask(__name__,
            static_url_path='',
            static_folder='web/static',
            template_folder='web/templates')


@app.route('/')
def index():
    text = data.markdown(open('web/index.md').read())
    return render_template('index.html', text=text)


@app.route('/app')
def application():
    return render_template('app.html', documentation=data.documentation)


@app.route('/app/data')
def app_data():
    return jsonify({'algorithms': data.algorithms, 'schemes': data.schemes})


@app.route('/app/compute-stage-1', methods=['POST'])
def compute_stage_1():
    # Fetch the selected values
    try:
        # TODO: Check for strictly positive etc.

        # Stage 1-A: Time block decomposition
        N = int(request.json['N'])
        tEnd = int(request.json['tEnd'])

        # Stage 1-B: base (fine) block propagator
        scheme = request.json['scheme']  # TODO: Check for string?
        if scheme not in data.schemes.keys():
            raise RuntimeError(
                f'scheme {scheme} unknown. Must be one of {data.schemes.keys()}'
            )
        M = int(request.json['M'])

        # Optional parameters
        points = request.json['points']
        quadType = request.json['quadType']
        form = request.json['form']
    except Exception as e:
        return jsonify({'error': f'[PARAM ERROR]\n{str(e)}'}), 500

    result = {}
    # Compute stuff here
    try:
        # TODO: Actually compute some stuff here
        result['delta_T'] = 0.2
        result['block_points_distribution'] = 15.2
        result['fine_discretization_error'] = 'I am a plot!'
        result['estimated_fine_block_cost'] = 8.3

    except Exception as e:
        return jsonify({'error': f'[COMPUTE ERROR]\n{str(e)}'}), 500

    return jsonify(result)


@app.route('/app/compute-stage-2', methods=['POST'])
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
                f'Algorithm {algo} unknown. Must be one of {data.algorithms.keys()}'
            )

        for param_dependency in data.algorithms[algo]:
            if request.json[param_depency] == None:
                raise RuntimeError(
                    f'Algorithm {algo} depends on the param {param_dependency} but is None.'
                )
    except Exception as e:
        return jsonify({'error': f'[PARAM ERROR]\n{str(e)}'}), 500

    result = {}
    # Compute stuff here
    try:
        # TODO: Actually compute some stuff here
        result['block_iteration'] = 7
        result['approximation_error'] = 'I am a plot!'
        result['coarse_error'] = 'I am a plot!'
        result['PinT_error'] = 'I am a plot!'
        result['PinT_iterations'] = 9
        result['PinT_speedup'] = 'I am a plot!'

    except Exception as e:
        return jsonify({'error': f'[COMPUTE ERROR]\n{str(e)}'}), 500

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

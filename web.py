#!/usr/bin/env python3

import json

from flask import Flask, jsonify, render_template, request

from web.utilities import compute_plot, fine_discretization_error

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

    print(json.dumps(request.json, indent=2))
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

        # Plot parameters
        reLambdaLow = float(request.json['reLambdaLow'])
        reLambdaHigh = float(request.json['reLambdaHigh'])
        imLambdaLow = float(request.json['imLambdaLow'])
        imLambdaHigh = float(request.json['imLambdaHigh'])
        nVals = int(request.json['nVals'])

        eMin = int(request.json['eMin'])
        eMax = int(request.json['eMax'])

    except Exception as e:
        return jsonify({'error': f'[PARAM ERROR]\n{str(e)}'}), 500

    result = {}
    # Compute stuff here
    try:
        # TODO: Actually compute some stuff here
        result['delta_T'] = 0.2
        result['block_points_distribution'] = 15.2
        result['fine_discretization_error'] = fine_discretization_error(
            N, tEnd, M, scheme, points, quadType, form, reLambdaLow,
            reLambdaHigh, imLambdaLow, imLambdaHigh, nVals, eMin, eMax)
        result['estimated_fine_block_cost'] = 5.2

    except Exception as e:
        return jsonify({'error': f'[COMPUTE ERROR]\n{str(e)}'}), 500

    return jsonify(result)


@app.route('/app/compute-stage-2', methods=['POST'])
def compute_stage_2():
    print(json.dumps(request.json, indent=2))
    # Fetch the selected values
    try:
        # TODO: Check for strictly positive etc.

        # Stage 2: Selection and analysis of a PinT algorithm
        algorithm = request.json['algorithm']
        if algorithm not in data.algorithms.keys():
            raise RuntimeError(
                f'Algorithm {algorithm} unknown. Must be one of {data.algorithms.keys()}'
            )

        for param_dependency in data.algorithms[algorithm]:
            if request.json[param_dependency] == None:
                raise RuntimeError(
                    f'Algorithm {algorithm} depends on the param {param_dependency} but is None.'
                )
    except Exception as e:
        return jsonify({'error': f'[PARAM ERROR]\n{type(e)}: {str(e)}'}), 500

    result = {}
    # Compute stuff here
    try:
        # TODO: Actually compute some stuff here
        result['block_iteration'] = 7
        result['approximation_error'] = compute_plot()
        result['coarse_error'] = compute_plot()
        result['PinT_error'] = compute_plot()
        result['PinT_iterations'] = 9
        result['PinT_speedup'] = compute_plot()

    except Exception as e:
        return jsonify({'error': f'[COMPUTE ERROR]\n{str(e)}'}), 500

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

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

allowed_schemes = ['COLLOCATION', 'RK4']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/compute', methods=['POST'])
def compute():
    # Fetch the selected values
    try:
        scheme = request.json['scheme']
        if scheme not in allowed_schemes:
            raise RuntimeError(
                f'scheme {scheme} unknown. Must be one of {allowed_schemes}')
        n = int(request.json['n'])
        N = int(request.json['N'])
        M = int(request.json['M'])
        n_steps_F = int(request.json['nStepsF'])
        n_steps_G = int(request.json['nStepsG'])
    except Exception as e:
        return jsonify({'error': f'[ERROR]\n{str(e)}'}), 500

    try:
        # Compute
        discretization_error_fig = discretization_error(scheme, n, N, M)
        pint_iter_fig = pint_iter(scheme, n, N, M, n_steps_F, n_steps_G)
        pint_error_fig = pint_error(scheme, n, N, M, n_steps_F, n_steps_G)
    except Exception as e:
        return jsonify({'error': f'[ERROR]\n{str(e)}'}), 500

    data = {
        'discretization': fig_to_dict(discretization_error_fig),
        'pint_iter': fig_to_dict(pint_iter_fig),
        'pint_error': fig_to_dict(pint_error_fig),
    }
    return jsonify({'data': data})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

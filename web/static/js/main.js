('use strict');

import { init } from './init.js';
import { elements } from './elements.js';
import { State } from './state.js';
import { Connection } from './connection.js';

// Create the global state
const state = new State(elements);

const connection = new Connection();

// Initialize all the elements with the state
init(elements, state, connection);

/*
// Send a message to the server by clicking on the compute button
document.getElementById('compute-button').onclick = () => {
  // Open up a compute message
  const notification = UIkit.notification({
    message: '<div uk-spinner></div> &nbsp; Computing...',
    pos: 'top-center',
    timeout: 0,
  });

  // Get the values
  const scheme = document.getElementById('select-scheme').value;
  const n = document.getElementById('select-n').value;
  const N = document.getElementById('select-N').value;
  const M = document.getElementById('select-M').value;
  const nStepsF = document.getElementById('select-n-steps-F').value;
  const nStepsG = document.getElementById('select-n-steps-G').value;
  const fetch_data = {
    scheme: scheme,
    n: n,
    N: N,
    M: M,
    nStepsF: nStepsF,
    nStepsG: nStepsG,
  };

  // Measure the time
  const startTime = performance.now();

  // Fetch the graph
  fetch('/compute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(fetch_data),
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      // Close the notification
      notification.close();

      if ('error' in data) {
        // Display an error
        UIkit.notification({
          message: `<span style="margin-left: 35%;">ERROR</span><br/>${data['error']}`,
          pos: 'top-center',
          status: 'danger',
          timeout: 5000,
        });
      } else {
        // Display taken time
        const endTime = performance.now();
        UIkit.notification({
          message: `Computation took ${endTime - startTime} ms`,
          pos: 'top-center',
          timeout: 3000,
        });

        // Get the plots
        const discretizationErrorDiv = document.getElementById(
          'discretization-error'
        );
        const pintIterDiv = document.getElementById('pint-iter');
        const pintErrorDiv = document.getElementById('pint-error');

        // Make them visible
        discretizationErrorDiv.style.display = 'block';
        pintIterDiv.style.display = 'block';
        pintErrorDiv.style.display = 'block';

        // Set their height
        const height =
          document.getElementById('selections-column').clientHeight;
        const heightString = `${height}px`;
        discretizationErrorDiv.style.height = heightString;
        pintIterDiv.style.height = heightString;
        pintErrorDiv.style.height = heightString;
        ['discretization', 'pint_iter', 'pint_error'].forEach((elem) => {
          data['data'][elem]['height'] = height - 100;
          data['data'][elem]['width'] =
            document.getElementById('plot-column').clientWidth - 100;
        });

        // Add the plots and their axis label
        discretizationErrorDiv.innerHTML =
          '<div id="discretization-plot"></div><div class="uk-text-meta uk-text-center">y-axis: `\\Im(\\lambda \\Delta T)` &nbsp;&nbsp;|&nbsp;&nbsp; x-axis: `\\Re(\\lambda \\Delta T)`</div>';
        mpld3.draw_figure(
          'discretization-plot',
          data['data']['discretization']
        );
        pintIterDiv.innerHTML =
          '<div id="pint-iter-plot"></div><div class="uk-text-meta uk-text-center">y-axis: `\\Im(\\lambda)` &nbsp;&nbsp;|&nbsp;&nbsp; x-axis: `\\Re(\\lambda)`</div>';
        mpld3.draw_figure('pint-iter-plot', data['data']['pint_iter']);
        pintErrorDiv.innerHTML =
          '<div id="pint-error-plot"></div><div class="uk-text-meta uk-text-center">y-axis: `\\Im(\\lambda \\Delta T)` &nbsp;&nbsp;|&nbsp;&nbsp; x-axis: `\\Re(\\lambda \\Delta T)`</div>';
        mpld3.draw_figure('pint-error-plot', data['data']['pint_error']);

        MathJax.typeset(); // Rerender new math equation

        // Then toggle the visibility
        const currentOption = document.getElementById('display-option').value;
        if (currentOption === 'discretization') {
          discretizationErrorDiv.style.display = 'block';
          pintIterDiv.style.display = 'none';
          pintErrorDiv.style.display = 'none';
        } else if (currentOption === 'pint-iter') {
          discretizationErrorDiv.style.display = 'none';
          pintIterDiv.style.display = 'block';
          pintErrorDiv.style.display = 'none';
        } else {
          discretizationErrorDiv.style.display = 'none';
          pintIterDiv.style.display = 'none';
          pintErrorDiv.style.display = 'block';
        }
      }
    })
    .catch((error) => {
      notification.close();
      alert(error);
    });
};

document.getElementById('display-option').onchange = () => {
  const discretizationErrorDiv = document.getElementById(
    'discretization-error'
  );
  const pintIterDiv = document.getElementById('pint-iter');
  const pintErrorDiv = document.getElementById('pint-error');

  // Set the correct visibility
  const currentOption = document.getElementById('display-option').value;
  if (currentOption === 'discretization') {
    discretizationErrorDiv.style.display = 'block';
    pintIterDiv.style.display = 'none';
    pintErrorDiv.style.display = 'none';
  } else if (currentOption === 'pint-iter') {
    discretizationErrorDiv.style.display = 'none';
    pintIterDiv.style.display = 'block';
    pintErrorDiv.style.display = 'none';
  } else {
    discretizationErrorDiv.style.display = 'none';
    pintIterDiv.style.display = 'none';
    pintErrorDiv.style.display = 'block';
  }
};
*/

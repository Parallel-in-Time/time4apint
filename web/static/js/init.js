('use strict');

function showError(error) {
  UIkit.notification({
    message: error,
    status: 'danger',
    pos: 'top-center',
    timeout: 5000,
  });
}
const computeNotification = {
  message: '<div uk-spinner></div> &nbsp; Computing...',
  pos: 'top-center',
  timeout: 0,
};

/**
 * Initialize all the onchange callbacks
 */
function init(elements, state, connection) {
  // --- Selections ---

  // TODO: Reset values on startup so that everything works fine

  // Initialize the algorithms and their default values correctly
  connection.initData().then((data) => {
    // Loop through algorithms
    Object.keys(data['algorithms']).forEach((algorithm) => {
      const opt = document.createElement('option');
      opt.value = algorithm;
      opt.innerHTML = algorithm;
      elements['algorithm'].appendChild(opt);
    });
    // Show the algorithm specific dependencies
    elements['algorithm'].onchange = () => {
      const currentSelection = elements['algorithm'].value;
      const dependencies = data['algorithms'][currentSelection];

      // Hide all dependency block
      elements[`schemeApproxParameters`].style.display = 'none';
      elements[`MCoarseParameters`].style.display = 'none';

      // Show the parameter selection block
      dependencies.forEach((dependency) => {
        elements[`${dependency}Parameters`].style = 'block';
      });

      state.update(); // Update the state in the end
    };

    // Loop through schemes and create options
    Object.keys(data['schemes']).forEach((scheme) => {
      const opt = document.createElement('option');
      opt.value = scheme;
      opt.innerHTML = scheme;
      elements['scheme'].appendChild(opt);
    });
    // Set the default values corresponding to the selected scheme on change
    elements['scheme'].onchange = () => {
      const currentSelection = elements['scheme'].value;
      const defaults = data['schemes'][currentSelection]['defaults'];

      // Set the default for all specified elements
      for (const [element, value] of Object.entries(defaults)) {
        elements[element].value = value;
      }

      state.update(); // Update the state in the end
    };

    // Update the state in the end
    state.update();
  });

  // Initialize the stage 1 button computation
  elements['stage1Button'].onclick = () => {
    const notification = UIkit.notification(computeNotification);
    const allSelections = state.getStageSelections(1);
    connection.compute(1, allSelections).then((data) => {
      notification.close();
      if ('error' in data) showError(data['error']);

      // Set the computed numbers
      elements['documentationBlockPointsDistribution'].innerHTML =
        'Block Points Distribution: `' +
        data['block_points_distribution'] +
        '`';
      elements['documentationDeltaT'].innerHTML =
        '`Delta T =' + data['delta_T'] + '`';
      elements['estimatedFineBlockCost'].value =
        data['estimated_fine_block_cost'];
      elements['stage1Output'].style.display = 'block';
      // Then rerender all injected math equations
      MathJax.typesetPromise();

      // Then create the plot
      Plotly.newPlot(
        elements['plotError'],
        JSON.parse(data['fine_discretization_error'])
      );
    });
  };

  // Initialize the stage 2 button computation
  elements['stage2Button'].onclick = () => {
    const notification = UIkit.notification(computeNotification);
    const allSelections = state.getStageSelections(2);
    connection.compute(2, allSelections).then((data) => {
      notification.close();
      if ('error' in data) showError(data['error']);

      // Set the content in the documentation column
      elements['blockIteration'].innerHTML =
        'Block iterations: `' + data['block_iteration'] + '`';
      elements['stage2Output'].style.display = 'block';
      // Then rerender all injected math equations
      MathJax.typesetPromise();

      // Then create the plots
      elements['plotTabIteration'].style.display = 'block';
      elements['plotTabEfficiency'].style.display = 'block';
      Plotly.newPlot(
        elements['plotIteration'],
        JSON.parse(data['approximation_error'])
      );

      Plotly.newPlot(
        elements['plotEfficiency'],
        JSON.parse(data['PinT_speedup'])
      );
      elements['plotTabIteration'].style.display = 'none';
      elements['plotTabEfficiency'].style.display = 'none';
      // TODO: Set the first tab activate
      // elements["plotSelection"].active(0);
    });
  };

  // Initialize all onchange elements that haven't been initialized yet
  // (algorithm and scheme are already set)
  elements['N'].onchange = () => state.update();
  elements['tEnd'].onchange = () => state.update();
  elements['M'].onchange = () => state.update();
  elements['points'].onchange = () => state.update();
  elements['quadType'].onchange = () => state.update();
  elements['form'].onchange = () => state.update();
  elements['schemeApproxPoints'].onchange = () => state.update();
  elements['schemeApproxForm'].onchange = () => state.update();
  elements['MCoarse'].onchange = () => state.update();

  // Then update the state view once
  state.update();

  // --- Plots ---
  // Change to the correct plot on tab selection
  elements['plotTabErrorSelection'].onclick = () => {
    elements['plotTabError'].style.display = 'block';
    elements['plotTabIteration'].style.display = 'none';
    elements['plotTabEfficiency'].style.display = 'none';
  };
  elements['plotTabIterationSelection'].onclick = () => {
    elements['plotTabError'].style.display = 'none';
    elements['plotTabIteration'].style.display = 'block';
    elements['plotTabEfficiency'].style.display = 'none';
  };
  elements['plotTabEfficiencySelection'].onclick = () => {
    elements['plotTabError'].style.display = 'none';
    elements['plotTabIteration'].style.display = 'none';
    elements['plotTabEfficiency'].style.display = 'block';
  };
}

export { init };

('use strict');

function showError(error) {
  UIkit.notification({
    message: error,
    status: 'danger',
    pos: 'top-center',
    timeout: 5000,
  });
}

/**
 * Initialize all the onchange callbacks
 */
function init(elements, state, connection) {
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
  });

  // Initialize the button events
  elements['stage1Button'].onclick = () => {
    const allSelections = state.getStageSelections(1);
    connection.compute(1, allSelections).then((data) => {
      if ('error' in data) showError(data['error']);

      // TODO: Pass this result on to the stage or to the plot renderer or something
      console.log(data);
      elements['documentationBlockPointsDistribution'].value =
        data['block_points_distribution'];
      elements['documentationDeltaT'].value = data['delta_T'];
      elements['stage1Output'].style.display = 'block';
    });
  };
  elements['stage2Button'].onclick = () => {
    const allSelections = state.getStageSelections(2);
    connection.compute(2, allSelections).then((data) => {
      if ('error' in data) showError(data['error']);

      // TODO: Pass this result on to the stage or to the plot renderer or something
      console.log(data);
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
}

export { init };

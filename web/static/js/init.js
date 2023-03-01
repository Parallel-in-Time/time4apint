('use strict');

/**
 * Initialize all the onchange callbacks
 */
function init(elements, state, connection) {
  // TODO: Initialize the algorithms correctly

  // Initialize the button events
  elements['stage1Button'].onclick = () => {
    connection.compute();
    state.compute(1); // TODO: Probably pass connection computation result on
  };

  // Initialize all onchange elements
  elements['N'].onchange = () => state.update();
  elements['tEnd'].onchange = () => state.update();
  elements['scheme'].onchange = () => state.update();
  elements['M'].onchange = () => state.update();
  elements['points'].onchange = () => state.update();
  elements['quadType'].onchange = () => state.update();
  elements['form'].onchange = () => state.update();
  elements['algorithm'].onchange = () => state.update();
  elements['schemeApproxPoints'].onchange = () => state.update();
  elements['schemeApproxForm'].onchange = () => state.update();
  elements['MCoarse'].onchange = () => state.update();

  // Then update the state view once
  state.update();
}

export { init };

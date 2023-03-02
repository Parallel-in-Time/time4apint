/**
 * All elements, so that they have the same name as the html id.
 */
const elements = {
  // Stage Elements
  stage1A: document.getElementById('stage-1-a'),
  stage1B: document.getElementById('stage-1-b'),
  stage2: document.getElementById('stage-2'),

  // Stage 2 dependencies
  schemeApproxParameters: document.getElementById('stage-2-schemeApprox'),
  MCoarseParameters: document.getElementById('stage-2-MCoarse'),

  // Buttons
  stage1Button: document.getElementById('stage-1-button'),
  stage2Button: document.getElementById('stage-2-button'),

  // Selection Elements
  N: document.getElementById('select-N'),
  tEnd: document.getElementById('select-tEnd'),
  scheme: document.getElementById('select-scheme'),
  M: document.getElementById('select-M'),
  points: document.getElementById('select-points'),
  quadType: document.getElementById('select-quadType'),
  form: document.getElementById('select-form'),
  algorithm: document.getElementById('select-algorithm'),
  schemeApproxPoints: document.getElementById('select-scheme-approx-points'),
  schemeApproxForm: document.getElementById('select-scheme-approx-form'),
  MCoarse: document.getElementById('select-MCoarse'),

  // TODO: Plot Elements
};

export { elements };

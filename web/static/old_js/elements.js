/**
 * All elements, so that they have the same name as the html id.
 */
const elements = {
  // Main columns
  documentation: document.getElementById('documentation'),
  selections: document.getElementById('selections'),
  plots: document.getElementById('plots'),

  // Stage Elements
  stage1A: document.getElementById('stage-1-a'),
  stage1B: document.getElementById('stage-1-b'),
  stage1Output: document.getElementById('stage-1-output'),
  stage2: document.getElementById('stage-2'),
  stage2Output: document.getElementById('stage-2-output'),
  stage1ADocumentation: document.getElementById('stage-1-a-documentation'),
  stage1BDocumentation: document.getElementById('stage-1-b-documentation'),
  stage2Documentation: document.getElementById('stage-2-documentation'),

  // Documentation outputs
  documentationBlockPointsDistribution: document.getElementById(
    'documentation-block-points-distribution'
  ),
  documentationDeltaT: document.getElementById('documentation-delta-T'),

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
  estimatedFineBlockCost: document.getElementById(
    'select-estimated-fine-block-cost'
  ),
  algorithm: document.getElementById('select-algorithm'),
  schemeApproxPoints: document.getElementById('select-scheme-approx-points'),
  schemeApproxForm: document.getElementById('select-scheme-approx-form'),
  MCoarse: document.getElementById('select-MCoarse'),
  blockIteration: document.getElementById('documentation-block-iteration'),

  // Plot Elements
  plotSelection: document.getElementById('plot-selection'),

  plotTabErrorSelection: document.getElementById('plot-tab-error-selection'),
  plotTabIterationSelection: document.getElementById(
    'plot-tab-iteration-selection'
  ),
  plotTabEfficiencySelection: document.getElementById(
    'plot-tab-efficiency-selection'
  ),

  plotTabError: document.getElementById('plot-tab-error'),
  plotTabIteration: document.getElementById('plot-tab-iteration'),
  plotTabEfficiency: document.getElementById('plot-tab-efficiency'),

  plotError: document.getElementById('plot-error'),
  plotIteration: document.getElementById('plot-iteration'),
  plotEfficiency: document.getElementById('plot-efficiency'),
};

export { elements };

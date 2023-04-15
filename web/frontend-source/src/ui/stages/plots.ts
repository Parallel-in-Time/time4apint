import { Parameter, makeParameterHTML } from './parameter.js';
import { getValueFromElement } from './html/common.js';
import { makePlotTabDiv, makeParameterGridDiv } from './html/plots_html.js';

class PlotsStage {
  public title: string;
  public id: string;
  public parameters: Array<Parameter>;
  public plot: string; // Sent as a string by the backend
  public plotObject: { [k: string]: any }; // String should be parsed as JSON
  public dependency: string;
  visible: boolean;

  /**
   * The constructor is empty so that a raw
   * object can be assigned to this class.
   */
  constructor() {
    this.title = '';
    this.id = '';
    this.parameters = [];
    this.plot = '';
    this.plotObject = {};
    this.dependency = '';
    this.visible = false;
  }

  /**
   * Initialize the visibility, which depends on whether
   * a dependency is set.
   */
  initializeVisibility(): void {
    this.visible = this.dependency === null || this.dependency === '';
  }

  /**
   * Collect all parameter values.
   */
  collect(): object {
    const parameters: { [k: string]: string } = {};
    this.parameters.forEach((parameter) => {
      parameters[parameter.id] = getValueFromElement(parameter.id);
    });
    return parameters;
  }

  /**
   * Generate the HTML divs of this stage.
   *
   * @returns The HTML div string.
   */
  async generate(): Promise<string> {
    // TODO: Dependency hook is ignored right now

    // Go through each parameter, get their values
    // and create their div.
    let parameterDivs = '';
    this.parameters.forEach((parameter) => {
      parameterDivs += makeParameterHTML(parameter);
    });

    const parameterGridDiv = makeParameterGridDiv(parameterDivs);
    return makePlotTabDiv(this.id, parameterGridDiv);
  }

  /**
   * Render a new plotly plot with 50% vertical height
   * if this stage contains a plot.
   */
  createPlot() {
    if (this.plot !== null) {
      this.plotObject = JSON.parse(this.plot);
      this.plotObject['config'] = { responsive: true };

      // Create the new plot and hope that plotly is loaded
      // @ts-expect-error
      Plotly.newPlot(`${this.id}-plot`, this.plotObject);

      // Call the resize to automatically adjust the plot sizes
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
      }, 50);
    }
  }
}

export { PlotsStage };

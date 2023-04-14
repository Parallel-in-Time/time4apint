import { Parameter, ParameterType } from './parameter.js';
import {
  makeSettingDiv,
  makeTitleDiv,
  makeNumberParameterDiv,
  makeTextParameterDiv,
  getValueFromElement,
  makeTextDiv,
  makeDocDiv,
  makePlotTabDiv,
  makeParameterGridDiv,
} from './html.js';

class DocsStage {
  public title: string;
  public id: string;
  public text: string;
  public dependency: string;
  visible: boolean;

  /**
   * The constructor is empty so that a raw
   * object can be assigned to this class.
   */
  constructor() {
    this.title = '';
    this.id = '';
    this.text = '';
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
   * Generate the HTML divs of this stage.
   *
   * @returns The HTML div string.
   */
  async generate(): Promise<string> {
    // TODO: Dependency hook is ignored right now
    const titleDiv = makeTitleDiv(this.title);
    const textDiv = makeTextDiv(this.text);

    // Create the inner html by concatenating the divs
    // and make the complete stage div.
    const inner = `${titleDiv}\n\n${textDiv}`;
    const docDiv = makeDocDiv(this.id, inner);
    return docDiv;
  }
}

class SettingsStage {
  public title: string;
  public id: string;
  public parameters: Array<Parameter>;
  public button: string;
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
    this.button = '';
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
      parameters[parameter.name] = getValueFromElement(parameter.id);
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
    const titleDiv = makeTitleDiv(this.title);

    // Go through each parameter, get their values
    // and create their div.
    let parameterDivs = '';
    this.parameters.forEach((parameter) => {
      let parameterDiv = '';
      const defaultValue =
        parameter.default === null ? '' : String(parameter.default);
      if (parameter.type == ParameterType.PositiveInteger) {
        parameterDiv = makeNumberParameterDiv(
          parameter.id,
          parameter.name,
          parameter.doc,
          defaultValue,
          parameter.values
        );
      } else {
        parameterDiv = makeTextParameterDiv(
          parameter.id,
          parameter.name,
          parameter.doc,
          defaultValue,
          parameter.values
        );
      }
      parameterDivs += parameterDiv;
    });

    // Create the inner html by concatenating the divs
    // and make the complete stage div.
    const inner = `${titleDiv}\n\n${parameterDivs}`;
    const settingDiv = makeSettingDiv(this.id, inner, this.button);
    return settingDiv;
  }
}

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
      parameters[parameter.name] = getValueFromElement(parameter.id);
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
      let parameterDiv = '';
      const defaultValue =
        parameter.default === null ? '' : String(parameter.default);
      if (parameter.type == ParameterType.PositiveInteger) {
        parameterDiv = makeNumberParameterDiv(
          parameter.id,
          parameter.name,
          parameter.doc,
          defaultValue,
          parameter.values
        );
      } else {
        parameterDiv = makeTextParameterDiv(
          parameter.id,
          parameter.name,
          parameter.doc,
          defaultValue,
          parameter.values
        );
      }
      parameterDivs += parameterDiv;
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
      // document
      //   .getElementById(`${this.id}-plot`)
      //   ?.setAttribute('style', 'height: 50vh');
      // Creatte the new plot and hope that plotly is loaded
      // @ts-expect-error
      Plotly.newPlot(`${this.id}-plot`, this.plotObject);
      console.log(
        `Created new Plot in '${this.id}-plot' with ${JSON.stringify(
          Object.keys(this.plotObject)
        )}`
      );
      window.dispatchEvent(new Event('resize')); // Call the resize to automatically adjust the plot sizes
    }
  }
}

export { DocsStage, SettingsStage, PlotsStage };

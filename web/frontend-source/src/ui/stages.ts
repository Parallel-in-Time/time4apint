import { Parameter, ParameterType } from './parameter.js';
import {
  makeSettingDiv,
  makeTitleDiv,
  makeNumberParameterDiv,
  makeTextParameterDiv,
  getValueFromElement,
  makeTextDiv,
  makeDocDiv,
} from './html.js';

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

export { SettingsStage, DocsStage };

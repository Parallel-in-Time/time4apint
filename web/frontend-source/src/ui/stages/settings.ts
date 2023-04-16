import { Parameter, makeParameterHTML } from './parameter.js';
// import { makeNumberParameterDiv, makeTextParameterDiv } from './html/html.js';

import { makeSettingDiv } from './html/settings_html.js';
import { makeTitleDiv, getValueFromElement } from './html/common.js';

class SettingsStage {
  public title: string;
  public id: string;
  public parameters: Array<Parameter>;
  public button: string;
  public dependency: string;
  public activated: boolean;
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
    this.activated = false;
    this.dependency = '';
    this.visible = true;
  }

  /**
   * Sets the visibility.
   * @param visibility Visibility of this stage.
   */
  setVisibility(visibility: boolean): void {
    this.visible = visibility;
  }

  /**
   * Whether this stage depends on another.
   * @returns True if this stage has a dependency.
   */
  hasDependency(): boolean {
    return !(this.dependency === null || this.dependency === '');
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
    const titleDiv = makeTitleDiv(this.title);

    // Go through each parameter, get their values
    // and create their div.
    let parameterDivs = '';
    this.parameters.forEach((parameter) => {
      parameterDivs += makeParameterHTML(parameter);
    });

    // Create the inner html by concatenating the divs
    // and make the complete stage div.
    const inner = `${titleDiv}\n\n${parameterDivs}`;
    const settingDiv = makeSettingDiv(this.id, inner, this.button);
    return settingDiv;
  }
}

export { SettingsStage };

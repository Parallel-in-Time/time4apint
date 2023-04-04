import { Parameter, ParameterType } from "./parameter.js";
import {
  makeStageDiv,
  makeTitleDiv,
  makeNumberDiv,
  makeTextDiv,
} from "./html.js";
import { slugify } from "../utils.js";

class SettingsStage {
  public title: string;
  public id: string;
  public parameters: Array<Parameter>;
  public dependency: string;

  constructor() {
    this.title = "";
    this.id = "";
    this.parameters = [];
    this.dependency = "";
  }

  async generate(): Promise<string> {
    // TODO: Dependency hook is ignored right now
    const titleDiv = makeTitleDiv(this.title);
    let parameterDivs = "";
    this.parameters.forEach((parameter) => {
      let parameterDiv = "";
      const id = slugify(parameter.name);
      const defaultValue =
        parameter.default === null ? "" : String(parameter.default);
      if (parameter.type == ParameterType.PositiveInteger) {
        parameterDiv = makeNumberDiv(
          id,
          parameter.name,
          parameter.doc,
          defaultValue,
          parameter.values
        );
      } else {
        parameterDiv = makeTextDiv(
          id,
          parameter.name,
          parameter.doc,
          defaultValue,
          parameter.values
        );
      }
      parameterDivs += parameterDiv;
    });

    const inner = `${titleDiv}\n\n${parameterDivs}`;
    const stageDiv = makeStageDiv(this.id, inner);
    return stageDiv;
  }
}

export { SettingsStage };

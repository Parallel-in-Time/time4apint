import { makePlotStageDiv } from './html.js';
import { DocsStage, SettingsStage, PlotsStage } from './stages.js';

/**
 * The components class contains all the information about the
 * received docs/settings/plots stages.
 * It also converts them initially to individual classes
 * and handles their generation, i.e., the HTML creation.
 * In addition, it is able to collect the data from the stages,
 * such as visible input parameters etc., that can then be
 * sent back to the backend.
 */
class Components {
  public docs: Array<DocsStage>;
  public settings: Array<SettingsStage>;
  public plots: Array<PlotsStage>;

  /**
   * The constructor is empty so that a raw
   * object can be assigned to this class.
   */
  constructor() {
    this.docs = [];
    this.settings = [];
    this.plots = [];
  }

  /**
   * Converts the stages initially from raw JSON objects
   * to individual classes that can keep track of the
   * application state.
   */
  async convertStages(): Promise<void> {
    // TODO: Probably make this asnyc

    // Convert the DocsStage
    // and make sure that they are invisible, if
    // the don't depend on any other stage.
    this.docs = this.docs.map((stage) => {
      // TODO: Don't overwrite existing ones
      const newStage = Object.assign(new DocsStage(), stage);
      newStage.initializeVisibility();
      return newStage;
    });

    // Convert the settings stages to SettingsStage
    this.settings = this.settings.map((stage) => {
      const newStage = Object.assign(new SettingsStage(), stage);
      newStage.initializeVisibility();
      return newStage;
    });

    // And then for plots
    this.plots = this.plots.map((stage) => {
      const newStage = Object.assign(new PlotsStage(), stage);
      newStage.initializeVisibility();
      return newStage;
    });
  }

  /**
   * Generate the docs HTML.
   *
   * @returns The generated docs HTML div.
   */
  async generateDocs(): Promise<string> {
    let docsDiv: string = '';
    // TODO: Async, instead of sync await?
    for (let i = 0; i < this.docs.length; i++) {
      docsDiv += await this.docs[i].generate();
    }
    return docsDiv;
  }

  /**
   * Generate the settings HTML.
   *
   * @returns The generated settings HTML div.
   */
  async generateSettings(): Promise<string> {
    let settingsDiv: string = '';
    // TODO: Async, instead of sync await?
    for (let i = 0; i < this.settings.length; i++) {
      settingsDiv += await this.settings[i].generate();
    }
    return settingsDiv;
  }

  /**
   * Generate the plots HTML.
   *
   * @returns The generated plots HTML div.
   */
  async generatePlots(): Promise<string> {
    let ids: Array<string> = [];
    let titles: Array<string> = [];
    let plotsDiv: string = '';
    // TODO: Async, instead of sync await?
    for (let i = 0; i < this.plots.length; i++) {
      plotsDiv += await this.plots[i].generate();
      ids.push(this.plots[i].id);
      titles.push(this.plots[i].title);
    }
    return makePlotStageDiv(ids, titles, plotsDiv);
  }

  /**
   * Render all the plots into their divs, if there is plot data.
   * This should be called after the `generatePlots()` already
   * created the HTML and this HTML is already injected into
   * the DOM.
   */
  async renderPlots(): Promise<void> {
    this.plots.forEach((plot) => plot.createPlot());
  }

  /**
   * Collect the data from all visible stages.
   *
   * @returns All stage parameters that are visible.
   */
  collect(): object {
    const settingStages = this.settings.filter((stage) => stage.visible);
    const settingsData: { [k: string]: object } = {};
    settingStages.forEach((stage) => {
      settingsData[stage.id] = stage.collect();
    });

    return {
      settings: settingsData,
    };
  }
}

export { Components };

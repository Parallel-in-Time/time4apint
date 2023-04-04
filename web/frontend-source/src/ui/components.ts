import { SettingsStage } from "./stages.js";

class Components {
  public docs: Array<number>;
  public settings: Array<SettingsStage>;
  public plots: Array<number>;
  constructor() {
    this.docs = [];
    this.settings = [];
    this.plots = [];
  }

  async convertStages(): Promise<void> {
    // TODO: Probably make this asnyc
    // TODO: Also for docs/plots
    this.settings = this.settings.map((stage) =>
      Object.assign(new SettingsStage(), stage)
    );
  }

  async generateDocs(): Promise<string> {
    console.log("Generatings docs");
    return "DOCS";
  }
  async generateSettings(): Promise<string> {
    console.log("Generatings settings");
    let settingsDiv: string = "";
    // TODO: Async, instead of sync await?
    for (let i = 0; i < this.settings.length; i++) {
      settingsDiv += await this.settings[i].generate();
    }
    return settingsDiv;
  }
  async generatePlots(): Promise<string> {
    console.log("Generatings plots");
    return "PLOTS";
  }
}

export { Components, SettingsStage };

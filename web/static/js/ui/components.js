var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { makePlotStageDiv } from './stages/html/plots_html.js';
import { DocsStage } from './stages/docs.js';
import { SettingsStage } from './stages/settings.js';
import { PlotsStage } from './stages/plots.js';
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
    /**
     * The constructor is empty so that a raw
     * object can be assigned to this class.
     */
    constructor() {
        Object.defineProperty(this, "docs", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "settings", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "plots", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        this.docs = [];
        this.settings = [];
        this.plots = [];
    }
    /**
     * Converts the stages initially from raw JSON objects
     * to individual classes that can keep track of the
     * application state.
     */
    convertStages() {
        return __awaiter(this, void 0, void 0, function* () {
            // TODO: Probably make this asnyc
            // Convert the DocsStage
            // and make sure that they are invisible, if
            // the don't depend on any other stage.
            this.docs = this.docs.map((stage) => {
                const newStage = Object.assign(new DocsStage(), stage);
                return newStage;
            });
            // Convert the settings stages to SettingsStage
            this.settings = this.settings.map((stage) => {
                const newStage = Object.assign(new SettingsStage(), stage);
                return newStage;
            });
            // And then for plots
            this.plots = this.plots.map((stage) => {
                const newStage = Object.assign(new PlotsStage(), stage);
                return newStage;
            });
            // And then check the the dependencies of all stages
            const docsList = this.docs;
            const stages = docsList.concat(this.settings).concat(this.plots);
            stages.forEach((stage) => {
                if (stage.hasDependency()) {
                    const dependency = stages.filter((s) => {
                        return s.id === stage.dependency;
                    });
                    if (dependency.length > 0) {
                        stage.setVisibility(dependency[0].activated);
                    }
                }
            });
        });
    }
    /**
     * Generate the docs HTML.
     *
     * @returns The generated docs HTML div.
     */
    generateDocs() {
        return __awaiter(this, void 0, void 0, function* () {
            let docsDiv = '';
            // TODO: Async, instead of sync await?
            for (let i = 0; i < this.docs.length; i++) {
                if (this.docs[i].visible) {
                    docsDiv += yield this.docs[i].generate();
                }
            }
            return docsDiv;
        });
    }
    /**
     * Generate the settings HTML.
     *
     * @returns The generated settings HTML div.
     */
    generateSettings() {
        return __awaiter(this, void 0, void 0, function* () {
            let settingsDiv = '';
            // TODO: Async, instead of sync await?
            for (let i = 0; i < this.settings.length; i++) {
                if (this.settings[i].visible) {
                    settingsDiv += yield this.settings[i].generate();
                }
            }
            return settingsDiv;
        });
    }
    /**
     * Generate the plots HTML.
     *
     * @returns The generated plots HTML div.
     */
    generatePlots() {
        return __awaiter(this, void 0, void 0, function* () {
            let ids = [];
            let titles = [];
            let plotsDiv = '';
            // TODO: Async, instead of sync await?
            for (let i = 0; i < this.plots.length; i++) {
                if (this.plots[i].visible) {
                    plotsDiv += yield this.plots[i].generate();
                    ids.push(this.plots[i].id);
                    titles.push(this.plots[i].title);
                }
            }
            return makePlotStageDiv(ids, titles, plotsDiv);
        });
    }
    /**
     * Render all the plots into their divs, if there is plot data.
     * This should be called after the `generatePlots()` already
     * created the HTML and this HTML is already injected into
     * the DOM.
     */
    renderPlots() {
        return __awaiter(this, void 0, void 0, function* () {
            this.plots.forEach((plot) => plot.createPlot());
        });
    }
    /**
     * Collect the data from all visible stages.
     *
     * @returns All stage parameters that are visible.
     */
    collect() {
        // Collect all settings parameters that are visible.
        const settingStages = this.settings.filter((stage) => stage.visible);
        const settingsData = {};
        settingStages.forEach((stage) => {
            settingsData[stage.id] = stage.collect();
        });
        // Collect all plot parameters.
        const plotsStages = this.plots.filter((stage) => stage.visible);
        const plotsData = {};
        plotsStages.forEach((stage) => {
            plotsData[stage.id] = stage.collect();
        });
        return {
            settings: settingsData,
            plots: plotsData,
        };
    }
}
export { Components };

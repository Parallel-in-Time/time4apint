var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { SettingsStage, DocsStage } from './stages.js';
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
            // TODO: Also for plots
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
                docsDiv += yield this.docs[i].generate();
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
                settingsDiv += yield this.settings[i].generate();
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
            console.log('Generatings plots');
            return 'PLOTS';
        });
    }
    /**
     * Collect the data from all visible stages.
     *
     * @returns All stage parameters that are visible.
     */
    collect() {
        const settingStages = this.settings.filter((stage) => stage.visible);
        const settingsData = {};
        settingStages.forEach((stage) => {
            settingsData[stage.id] = stage.collect();
        });
        return {
            settings: settingsData,
        };
    }
}
export { Components, SettingsStage };

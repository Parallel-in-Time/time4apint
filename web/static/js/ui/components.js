var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { SettingsStage } from "./stages.js";
class Components {
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
    convertStages() {
        return __awaiter(this, void 0, void 0, function* () {
            // TODO: Probably make this asnyc
            // TODO: Also for docs/plots
            this.settings = this.settings.map((stage) => Object.assign(new SettingsStage(), stage));
        });
    }
    generateDocs() {
        return __awaiter(this, void 0, void 0, function* () {
            console.log("Generatings docs");
            return "DOCS";
        });
    }
    generateSettings() {
        return __awaiter(this, void 0, void 0, function* () {
            console.log("Generatings settings");
            let settingsDiv = "";
            // TODO: Async, instead of sync await?
            for (let i = 0; i < this.settings.length; i++) {
                settingsDiv += yield this.settings[i].generate();
            }
            return settingsDiv;
        });
    }
    generatePlots() {
        return __awaiter(this, void 0, void 0, function* () {
            console.log("Generatings plots");
            return "PLOTS";
        });
    }
}
export { Components, SettingsStage };

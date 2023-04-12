var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { ParameterType } from './parameter.js';
import { makeSettingDiv, makeTitleDiv, makeNumberParameterDiv, makeTextParameterDiv, getValueFromElement, makeTextDiv, makeDocDiv, makePlotTabDiv, } from './html.js';
class DocsStage {
    /**
     * The constructor is empty so that a raw
     * object can be assigned to this class.
     */
    constructor() {
        Object.defineProperty(this, "title", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "id", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "text", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "dependency", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "visible", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
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
    initializeVisibility() {
        this.visible = this.dependency === null || this.dependency === '';
    }
    /**
     * Generate the HTML divs of this stage.
     *
     * @returns The HTML div string.
     */
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
            // TODO: Dependency hook is ignored right now
            const titleDiv = makeTitleDiv(this.title);
            const textDiv = makeTextDiv(this.text);
            // Create the inner html by concatenating the divs
            // and make the complete stage div.
            const inner = `${titleDiv}\n\n${textDiv}`;
            const docDiv = makeDocDiv(this.id, inner);
            return docDiv;
        });
    }
}
class SettingsStage {
    /**
     * The constructor is empty so that a raw
     * object can be assigned to this class.
     */
    constructor() {
        Object.defineProperty(this, "title", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "id", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "parameters", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "button", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "dependency", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "visible", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
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
    initializeVisibility() {
        this.visible = this.dependency === null || this.dependency === '';
    }
    /**
     * Collect all parameter values.
     */
    collect() {
        const parameters = {};
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
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
            // TODO: Dependency hook is ignored right now
            const titleDiv = makeTitleDiv(this.title);
            // Go through each parameter, get their values
            // and create their div.
            let parameterDivs = '';
            this.parameters.forEach((parameter) => {
                let parameterDiv = '';
                const defaultValue = parameter.default === null ? '' : String(parameter.default);
                if (parameter.type == ParameterType.PositiveInteger) {
                    parameterDiv = makeNumberParameterDiv(parameter.id, parameter.name, parameter.doc, defaultValue, parameter.values);
                }
                else {
                    parameterDiv = makeTextParameterDiv(parameter.id, parameter.name, parameter.doc, defaultValue, parameter.values);
                }
                parameterDivs += parameterDiv;
            });
            // Create the inner html by concatenating the divs
            // and make the complete stage div.
            const inner = `${titleDiv}\n\n${parameterDivs}`;
            const settingDiv = makeSettingDiv(this.id, inner, this.button);
            return settingDiv;
        });
    }
}
class PlotsStage {
    /**
     * The constructor is empty so that a raw
     * object can be assigned to this class.
     */
    constructor() {
        Object.defineProperty(this, "title", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "id", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "parameters", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "plot", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "dependency", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "visible", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        this.title = '';
        this.id = '';
        this.parameters = [];
        this.plot = {};
        this.dependency = '';
        this.visible = false;
    }
    /**
     * Initialize the visibility, which depends on whether
     * a dependency is set.
     */
    initializeVisibility() {
        this.visible = this.dependency === null || this.dependency === '';
    }
    /**
     * Collect all parameter values.
     */
    collect() {
        const parameters = {};
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
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
            // TODO: Dependency hook is ignored right now
            // Go through each parameter, get their values
            // and create their div.
            let parameterDivs = '';
            this.parameters.forEach((parameter) => {
                let parameterDiv = '';
                const defaultValue = parameter.default === null ? '' : String(parameter.default);
                if (parameter.type == ParameterType.PositiveInteger) {
                    parameterDiv = makeNumberParameterDiv(parameter.id, parameter.name, parameter.doc, defaultValue, parameter.values);
                }
                else {
                    parameterDiv = makeTextParameterDiv(parameter.id, parameter.name, parameter.doc, defaultValue, parameter.values);
                }
                parameterDivs += parameterDiv;
            });
            return makePlotTabDiv(this.id, parameterDivs);
        });
    }
    /**
     * Render a new plotly plot with 50% vertical height
     * if this stage contains a plot.
     */
    createPlot() {
        var _a;
        if (this.plot !== null) {
            (_a = document
                .getElementById(`${this.id}-plot`)) === null || _a === void 0 ? void 0 : _a.setAttribute('style', 'height: 50vh');
            // Creatte the new plot and hope that plotly is loaded
            // @ts-expect-error
            Plotly.newPlot(`${this.id}-plot`, this.plot);
        }
    }
}
export { DocsStage, SettingsStage, PlotsStage };

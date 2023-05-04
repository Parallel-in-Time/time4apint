var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { makeParameterHTML } from './parameter.js';
import { getValueFromElement } from './html/common.js';
import { makePlotTabDiv, makeParameterGridDiv } from './html/plots_html.js';
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
        }); // Sent as a string by the backend
        Object.defineProperty(this, "plotObject", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        }); // String should be parsed as JSON
        Object.defineProperty(this, "activated", {
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
        this.plot = '';
        this.plotObject = {};
        this.activated = false;
        this.dependency = '';
        this.visible = true;
    }
    /**
     * Sets the visibility.
     * @param visibility Visibility of this stage.
     */
    setVisibility(visibility) {
        this.visible = visibility;
    }
    /**
     * Whether this stage depends on another.
     * @returns True if this stage has a dependency.
     */
    hasDependency() {
        return !(this.dependency === null || this.dependency === '');
    }
    /**
     * Collect all parameter values.
     */
    collect() {
        const parameters = {};
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
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
            // Go through each parameter, get their values
            // and create their div.
            let parameterDivs = '';
            this.parameters.forEach((parameter) => {
                parameterDivs += makeParameterHTML(parameter);
            });
            const parameterGridDiv = makeParameterGridDiv(parameterDivs);
            return makePlotTabDiv(this.id, parameterGridDiv);
        });
    }
    /**
     * Render a new plotly plot with 50% vertical height
     * if this stage contains a plot.
     */
    createPlot() {
        if (this.plot !== null) {
            this.plotObject = JSON.parse(this.plot);
            this.plotObject['config'] = { responsive: true };
            // Empty the plot div and create a new plot and hope that plotly is loaded
            const plotDiv = document.getElementById(`${this.id}-plot`);
            if (plotDiv !== null) {
                plotDiv.innerHTML = '';
                // @ts-expect-error
                Plotly.newPlot(plotDiv, this.plotObject);
                // Plotly.newPlot(`${this.id}-plot`, this.plotObject);
            }
            // Call the resize to automatically adjust the plot sizes
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
            }, 50);
        }
    }
}
export { PlotsStage };

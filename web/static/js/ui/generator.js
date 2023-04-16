var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { sendData } from '../connection.js';
import { Components } from './components.js';
import { setInputOnChangeCallbacks } from './stages/parameter.js';
class Generator {
    constructor() {
        Object.defineProperty(this, "components", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        Object.defineProperty(this, "initialized", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        this.components = new Components();
        this.initialized = false;
    }
    /**
     * Generates the UI from the components that were sent by the server.
     *
     * @param response The components received from the backend.
     */
    makeUI(response) {
        return __awaiter(this, void 0, void 0, function* () {
            // Initialize the components for the first time
            if (!this.initialized) {
                this.components = Object.assign(this.components, response);
            }
            else {
                // Otherwise append currently unknown components
                const newComponents = new Components();
                Object.assign(newComponents, response);
            }
            yield this.components.convertStages();
            this.generate();
        });
    }
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
            const [docsDiv, settingsDiv, plotsDiv] = yield Promise.all([
                this.components.generateDocs(),
                this.components.generateSettings(),
                this.components.generatePlots(),
            ]);
            // Inject all the HTML divs
            const documentationHTML = document.getElementById('documentation');
            if (documentationHTML !== null) {
                documentationHTML.innerHTML = docsDiv;
            }
            const settingsHTML = document.getElementById('settings');
            if (settingsHTML !== null) {
                settingsHTML.innerHTML = settingsDiv;
            }
            const plotsHTML = document.getElementById('plot');
            if (plotsHTML !== null) {
                plotsHTML.innerHTML = plotsDiv;
                this.components.renderPlots();
            }
            // Set the button callbacks to send the data back
            this.setButtonsCallback();
            // Set the input element onchange callbacks for type checking (>0 etc.)
            setInputOnChangeCallbacks();
            // Render math equations
            // @ts-expect-error
            MathJax.typesetPromise();
        });
    }
    /**
     * Collect the component data, send it and
     * make the UI again with the response.
     */
    collectAndSendData() {
        sendData(this.components.collect()).then((response) => {
            // Alert if there is an error
            if ('error' in response) {
                alert(response);
                return;
            }
            this.makeUI(response);
        });
    }
    /**
     * Sets the callbacks for all buttons to collect and
     * send the data to the backend.
     */
    setButtonsCallback() {
        return __awaiter(this, void 0, void 0, function* () {
            const stageButtons = document.getElementsByClassName('data-callback-button');
            for (let i = 0; i < stageButtons.length; i++) {
                // On hover check whether there are any visible danger elements
                stageButtons[i].addEventListener('mouseover', (event) => {
                    if (event.target instanceof HTMLButtonElement) {
                        if (document.getElementsByClassName('uk-form-danger').length > 0) {
                            event.target.disabled = true;
                        }
                        else {
                            event.target.disabled = false;
                        }
                    }
                });
                // On click collect and send all the visible data elements
                stageButtons[i].addEventListener('click', () => this.collectAndSendData());
            }
        });
    }
}
export { Generator };

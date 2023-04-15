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
class Generator {
    constructor() {
        Object.defineProperty(this, "components", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        this.components = new Components();
    }
    makeUI(response) {
        return __awaiter(this, void 0, void 0, function* () {
            this.components = Object.assign(this.components, response);
            console.log(this.components);
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
            }
            this.setButtonsCallback();
        });
    }
    /**
     * Collect the component data, send it and
     * make the UI again with the response.
     */
    collectAndSendData() {
        console.log('Sending data...');
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
                stageButtons[i].addEventListener('click', () => this.collectAndSendData());
            }
        });
    }
}
export { Generator };
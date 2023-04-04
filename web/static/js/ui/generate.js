var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { Components } from "./components.js";
function generate(response) {
    return __awaiter(this, void 0, void 0, function* () {
        const components = Object.assign(new Components(), response);
        yield components.convertStages();
        console.log(components);
        const [docsDiv, settingsDiv, plotsDiv] = yield Promise.all([
            components.generateDocs(),
            components.generateSettings(),
            components.generatePlots(),
        ]);
        console.log(settingsDiv);
        const documentationHTML = document.getElementById("documentation");
        if (documentationHTML !== null) {
            documentationHTML.innerHTML = docsDiv;
        }
        const settingsHTML = document.getElementById("settings");
        if (settingsHTML !== null) {
            settingsHTML.innerHTML = settingsDiv;
        }
        const plotsHTML = document.getElementById("plot");
        if (plotsHTML !== null) {
            plotsHTML.innerHTML = plotsDiv;
        }
    });
}
export { generate };

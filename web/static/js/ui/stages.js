var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { ParameterType } from "./parameter.js";
import { makeStageDiv, makeTitleDiv, makeNumberDiv, makeTextDiv, } from "./html.js";
import { slugify } from "../utils.js";
class SettingsStage {
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
        Object.defineProperty(this, "dependency", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        this.title = "";
        this.id = "";
        this.parameters = [];
        this.dependency = "";
    }
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
            // TODO: Dependency hook is ignored right now
            const titleDiv = makeTitleDiv(this.title);
            let parameterDivs = "";
            this.parameters.forEach((parameter) => {
                let parameterDiv = "";
                const id = slugify(parameter.name);
                const defaultValue = parameter.default === null ? "" : String(parameter.default);
                if (parameter.type == ParameterType.PositiveInteger) {
                    parameterDiv = makeNumberDiv(id, parameter.name, parameter.doc, defaultValue, parameter.values);
                }
                else {
                    parameterDiv = makeTextDiv(id, parameter.name, parameter.doc, defaultValue, parameter.values);
                }
                parameterDivs += parameterDiv;
            });
            const inner = `${titleDiv}\n\n${parameterDivs}`;
            const stageDiv = makeStageDiv(this.id, inner);
            return stageDiv;
        });
    }
}
export { SettingsStage };

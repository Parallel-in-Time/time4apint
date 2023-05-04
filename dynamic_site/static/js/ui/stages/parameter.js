var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { makeIntegerParameterDiv, makePositiveIntegerParameterDiv, makeStrictlyPositiveIntegerParameterDiv, makePositiveFloatParameterDiv, makeFloatParameterDiv, makeEnumerationParameterDiv, makeFloatListParameterDiv, makeBooleanParameterDiv, } from './html/parameter_html.js';
var ParameterType;
(function (ParameterType) {
    ParameterType["Integer"] = "Integer";
    ParameterType["PositiveInteger"] = "PositiveInteger";
    ParameterType["StrictlyPositiveInteger"] = "StrictlyPositiveInteger";
    ParameterType["PositiveFloat"] = "PositiveFloat";
    ParameterType["Float"] = "Float";
    ParameterType["FloatList"] = "FloatList";
    ParameterType["Enumeration"] = "Enumeration";
    ParameterType["Boolean"] = "Boolean";
})(ParameterType || (ParameterType = {}));
function getParameterTypeId(type) {
    return (type[0].toLowerCase() +
        type
            .slice(1, type.length)
            .replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`));
}
function makeParameterHTML(param) {
    var _a;
    const id = param.id;
    const name = param.name;
    const doc = param.doc;
    const defaultValue = param.default === null ? '' : String(param.default);
    const placeholder = param.placeholder;
    switch (param.type) {
        case ParameterType.Integer:
            return makeIntegerParameterDiv(id, name, doc, defaultValue, placeholder);
        case ParameterType.PositiveInteger:
            return makePositiveIntegerParameterDiv(id, name, doc, defaultValue, placeholder);
        case ParameterType.StrictlyPositiveInteger:
            return makeStrictlyPositiveIntegerParameterDiv(id, name, doc, defaultValue, placeholder);
        case ParameterType.PositiveFloat:
            return makePositiveFloatParameterDiv(id, name, doc, defaultValue, placeholder);
        case ParameterType.Float:
            return makeFloatParameterDiv(id, name, doc, defaultValue, placeholder);
        case ParameterType.FloatList:
            return makeFloatListParameterDiv(id, name, doc, defaultValue, placeholder);
        case ParameterType.Enumeration:
            return makeEnumerationParameterDiv(id, name, doc, (_a = param.choices) !== null && _a !== void 0 ? _a : [], defaultValue);
        case ParameterType.Boolean:
            makeBooleanParameterDiv(id, name, doc, defaultValue === 'true');
        default:
            console.error(`ERROR: ${param.type} did not occur in the the switch case`);
            return 'error';
    }
}
function setInputOnChangeCallback(className, fn) {
    return __awaiter(this, void 0, void 0, function* () {
        const inputs = document.getElementsByClassName(className);
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].addEventListener('change', (event) => {
                if (event.target instanceof HTMLElement) {
                    fn(event.target);
                }
            });
        }
    });
}
/**
 * Set the input callback that check onchange
 * of any of the set inputs whether they are valid,
 * i.e., strictly positive etc.
 */
function setInputOnChangeCallbacks() {
    return __awaiter(this, void 0, void 0, function* () {
        const addClass = (target) => {
            target.classList.add('uk-form-danger');
        };
        const removeClass = (target) => {
            target.classList.remove('uk-form-danger');
        };
        // Integer
        setInputOnChangeCallback(getParameterTypeId(ParameterType.Integer), (target) => {
            removeClass(target);
        });
        // PositiveInteger
        setInputOnChangeCallback(getParameterTypeId(ParameterType.PositiveInteger), (target) => {
            if (+target.value < 0) {
                addClass(target);
            }
            else {
                removeClass(target);
            }
        });
        // StrictlyPositiveInteger
        setInputOnChangeCallback(getParameterTypeId(ParameterType.StrictlyPositiveInteger), (target) => {
            if (+target.value <= 0) {
                addClass(target);
            }
            else {
                removeClass(target);
            }
        });
        // PositiveFloat
        setInputOnChangeCallback(getParameterTypeId(ParameterType.PositiveFloat), (target) => {
            if (+target.value < 0) {
                addClass(target);
            }
            else {
                removeClass(target);
            }
        });
        // Float
        setInputOnChangeCallback(getParameterTypeId(ParameterType.Float), (target) => {
            removeClass(target);
        });
        // FloatList
        setInputOnChangeCallback(getParameterTypeId(ParameterType.FloatList), (target) => {
            // TODO: Check with a regex, whether this is a list of floats!
            removeClass(target);
        });
        // Enumeration
        setInputOnChangeCallback(getParameterTypeId(ParameterType.Enumeration), (_) => { });
        // Boolean
        setInputOnChangeCallback(getParameterTypeId(ParameterType.Boolean), (_) => { });
    });
}
export { ParameterType, getParameterTypeId, makeParameterHTML, setInputOnChangeCallbacks, };

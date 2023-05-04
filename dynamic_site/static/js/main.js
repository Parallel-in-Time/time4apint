var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { Generator } from './ui/generator.js';
import { fetchComponents } from './connection.js';
function main() {
    return __awaiter(this, void 0, void 0, function* () {
        // Fetch the components
        const response = yield fetchComponents();
        // Alert if there is an error
        if ('error' in response) {
            alert(response.response);
            return;
        }
        // Otherwise display the components properly
        const generator = new Generator();
        generator.makeUI(response);
    });
}
main();
console.log('If this message is shown, everything is\n\n       ===> PinTastic <===\n ');

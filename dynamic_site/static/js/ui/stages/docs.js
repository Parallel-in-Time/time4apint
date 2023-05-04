var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { makeTextDiv, makeDocDiv } from './html/docs_html.js';
import { makeTitleDiv } from './html/common.js';
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
        Object.defineProperty(this, "activated", {
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
     * Generate the HTML divs of this stage.
     *
     * @returns The HTML div string.
     */
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
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
export { DocsStage };

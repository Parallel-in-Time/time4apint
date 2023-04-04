var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
function fetch_components() {
    return __awaiter(this, void 0, void 0, function* () {
        // Fetch the initialization components
        const response = yield fetch("/app/components", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });
        if (!response.ok) {
            // TODO: Handle the error message
            console.log("Error with the response:", response);
            return { error: "Error" };
        }
        // Handle the response here
        if (response.body !== null) {
            const body = yield response.json();
            return body;
        }
    });
}
export { fetch_components };

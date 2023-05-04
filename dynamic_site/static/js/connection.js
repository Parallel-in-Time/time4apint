var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
function fetchComponents() {
    return __awaiter(this, void 0, void 0, function* () {
        const body = yield sendData({});
        return body;
        // Fetch the initialization components
        const response = yield fetch(`${window.location.href}/compute`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            // TODO: Handle the error message
            console.log('Error with the response:', response);
            return { error: 'Error' };
        }
        // Get the json from the response and return it.
        if (response.body !== null) {
            const body = yield response.json();
            return body;
        }
    });
}
/**
 * Send the data to the /app/compute path of the backend.
 *
 * @param data The JSON object to send back.
 * @returns The response as a json object (has 'error' as a key if there is an error).
 */
function sendData(data) {
    return __awaiter(this, void 0, void 0, function* () {
        // Post the data to the given url
        const response = yield fetch(`${window.location.href}/compute`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            },
            referrerPolicy: 'no-referrer',
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            // TODO: Handle the error message
            console.log('Error with the response:', response);
            return { error: 'Error' };
        }
        // Get the json from the response and return it.
        if (response.body !== null) {
            const body = yield response.json();
            return body;
        }
    });
}
export { fetchComponents, sendData };

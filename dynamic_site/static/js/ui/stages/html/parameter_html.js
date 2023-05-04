import { ParameterType, getParameterTypeId } from '../parameter.js';
// ----------------------------------
// Number fields
function makeNumberParameterDiv(id, type, name, doc, defaultValue, placeholder, className, options) {
    // TODO: Count the tabindex up -> tabindex="5"
    // TODO: required=true ?
    return `
  <div class="uk-margin-small-left" uk-grid>
    <span
      class="uk-margin-small-right uk-margin-small-top"
      >${name}:
    </span>
    <div class="uk-width-expand@m uk-padding-remove-left">
      <input
        uk-tooltip="title: ${doc}"
        class="uk-input uk-align-right ${defaultValue === '' ? 'uk-form-danger' : ''} ${className}"
        id="select-${id}"
        type="${type}"
        value="${defaultValue}"
        placeholder="${placeholder}"
        required="true"
        ${options}
      />
    </div>
  </div>`;
}
function makeIntegerParameterDiv(id, name, doc, defaultValue, placeholder) {
    return makeNumberParameterDiv(id, 'number', name, doc, defaultValue, placeholder, getParameterTypeId(ParameterType.Integer), `step="1"`);
}
function makePositiveIntegerParameterDiv(id, name, doc, defaultValue, placeholder) {
    return makeNumberParameterDiv(id, 'number', name, doc, defaultValue, placeholder, getParameterTypeId(ParameterType.PositiveInteger), `step="1"\nmin="0"`);
}
function makeStrictlyPositiveIntegerParameterDiv(id, name, doc, defaultValue, placeholder) {
    return makeNumberParameterDiv(id, 'number', name, doc, defaultValue, placeholder, getParameterTypeId(ParameterType.StrictlyPositiveInteger), `step="1"\nmin="1"`);
}
function makeFloatParameterDiv(id, name, doc, defaultValue, placeholder) {
    return makeNumberParameterDiv(id, 'number', name, doc, defaultValue, placeholder, getParameterTypeId(ParameterType.Float), '');
}
function makePositiveFloatParameterDiv(id, name, doc, defaultValue, placeholder) {
    return makeNumberParameterDiv(id, 'number', name, doc, defaultValue, placeholder, getParameterTypeId(ParameterType.PositiveFloat), `min="0"`);
}
function makeFloatListParameterDiv(id, name, doc, defaultValue, placeholder) {
    // TODO: Make regex to check for float only params
    return `
  <div class="uk-margin-small-left" uk-grid>
    <span
      class="uk-margin-small-right uk-margin-small-top"
      >${name}:
    </span>
    <div class="uk-width-expand@m uk-padding-remove-left">
      <input
        uk-tooltip="title: ${doc}"
        class="uk-input uk-align-right ${defaultValue === '' ? 'uk-form-danger' : ''} ${getParameterTypeId(ParameterType.FloatList)}"
        id="select-${id}"
        type="text"
        value="${defaultValue}"
        placeholder="${placeholder}"
      />
    </div>
  </div>`;
}
// -----------------------------
// Enumeration
function makeEnumerationParameterDiv(id, name, doc, choices, defaultValue) {
    let options = '';
    choices.forEach((choice) => {
        options += `<option ${defaultValue === choice ? 'selected="selected"' : ''} value="${choice}">${choice}</option>\n`;
    });
    // A dropdown
    return `
    <div class="uk-margin-small-left" uk-grid>
      <span class="uk-margin-small-right uk-margin-small-top"
        >${name}
      </span>
      <div class="uk-width-expand@m uk-padding-remove-left">
        <select
          id="select-${id}"
          class="uk-select ${getParameterTypeId(ParameterType.Enumeration)}"
          uk-tooltip="title: ${doc}"
        >
          ${options}
        </select>
      </div>
    </div>
    `;
}
// -----------------------------
// Checkbox
function makeBooleanParameterDiv(id, name, doc, checked) {
    const defaultChecked = checked ? 'checked' : '';
    return `
    <div class="uk-margin-small-left" uk-grid>
      <span class="uk-margin-small-right uk-margin-small-top"
        >${name}
      </span>
      <div class="uk-width-expand@m uk-padding-remove-left">
        <input
            uk-tooltip="title: ${doc}"
            id="select-${id}"
            class="uk-checkbox ${getParameterTypeId(ParameterType.Boolean)}"
            type="checkbox"
        ${defaultChecked}>
      </div>
    </div>
    `;
}
export { makeIntegerParameterDiv, makePositiveIntegerParameterDiv, makeStrictlyPositiveIntegerParameterDiv, makePositiveFloatParameterDiv, makeFloatParameterDiv, makeEnumerationParameterDiv, makeFloatListParameterDiv, makeBooleanParameterDiv, };

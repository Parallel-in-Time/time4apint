function makeStageDiv(id, inner, button) {
    const buttonDiv = button !== null
        ? `
<button
  id="${id}-button"
  class="uk-width-expand uk-button uk-button-default data-callback-button"      
>${button}</button>`
        : '';
    return `
<div
    id="${id}"
    class="uk-grid-small uk-child-width-1-1"
    uk-grid
    >
    ${inner}
    <div>
    ${buttonDiv}
    </div>
</div>`;
}
function makeSettingDiv(id, inner, button) {
    return makeStageDiv(id, inner, button);
}
function makeDocDiv(id, inner) {
    return makeStageDiv(id, inner, null);
}
function makePlotStageDiv(ids, titles, inner) {
    let tabs = '';
    for (let i = 0; i < ids.length; i++) {
        tabs += makePlotTabTitleDiv(ids[i], titles[i], i == 0);
    }
    return `
<ul id="plot-selection" class="uk-child-width-expand" uk-tab>
  ${tabs}
</ul>
${inner}
`;
}
function makePlotTabTitleDiv(id, title, active) {
    return `
  <li class="${active ? 'uk-active' : ''}">
    <a id="${id}">${title}</a>
  </li>`;
}
function makePlotTabDiv(id, parameter) {
    return `
<div id="${id}">
  <div id="${id}-plot"></div>
  ${parameter}
</div>`;
}
function makeTitleDiv(title) {
    return `
<div class="uk-heading-bullet uk-margin-small-top uk-text-bolder" >
${title}
</div>
`;
}
function makeNumberParameterDiv(id, name, doc, defaultValue, placeholder) {
    return makeParameterDiv(id, 'number', name, doc, defaultValue, placeholder);
}
function makeTextParameterDiv(id, name, doc, defaultValue, placeholder) {
    return makeParameterDiv(id, 'text', name, doc, defaultValue, placeholder);
}
function makeTextDiv(text) {
    return `
<div>
  ${text}
</div>`;
}
function makeParameterDiv(id, type, name, doc, defaultValue, placeholder) {
    // TODO: Count the tabindex up -> tabindex="5"
    return `
<div class="uk-margin-small-left" uk-grid>
  <span
    class="uk-margin-small-right uk-margin-small-top"
    >${name}:
  </span>
  <div class="uk-width-expand@m uk-padding-remove-left">
    <input
      uk-tooltip="title: ${doc}"
      class="uk-input uk-align-right"
      id="select-${id}"
      type="${type}"
      value="${defaultValue}"
      placeholder="${placeholder}"
    />
  </div>
</div>`;
}
/**
 * Gets the value from an HTML input field.
 *
 * @param id The unique id of the parameter.
 * @returns The input values as a string.
 */
function getValueFromElement(id) {
    return document.getElementById(`select-${id}`).value;
}
export { makeSettingDiv, makeDocDiv, makeTitleDiv, makePlotTabDiv, makePlotStageDiv, makeNumberParameterDiv, makeTextParameterDiv, makeTextDiv, getValueFromElement, };

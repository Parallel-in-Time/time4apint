function makeStageDiv(id, inner) {
    return `
<div
    id="${id}"
    class="uk-grid-small uk-child-width-1-1"
    uk-grid
    >
    ${inner}
</div>`;
}
function makeTitleDiv(title) {
    return `
<div class="uk-heading-bullet uk-margin-small-top uk-text-bolder" >
${title}
</div>
`;
}
function makeNumberDiv(id, name, doc, defaultValue, placeholder) {
    return makeParameterDiv(id, "number", name, doc, defaultValue, placeholder);
}
function makeTextDiv(id, name, doc, defaultValue, placeholder) {
    return makeParameterDiv(id, "text", name, doc, defaultValue, placeholder);
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
      uk-tooltip="title: ${doc}."
      class="uk-input uk-align-right"
      id="select-${id}"
      type="${type}"
      value="${defaultValue}"
      placeholder="${placeholder}"
    />
  </div>
</div>`;
}
export { makeStageDiv, makeTitleDiv, makeNumberDiv, makeTextDiv };

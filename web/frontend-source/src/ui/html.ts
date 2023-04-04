function makeStageDiv(id: string, inner: string): string {
  return `
<div
    id="${id}"
    class="uk-grid-small uk-child-width-1-1"
    uk-grid
    >
    ${inner}
</div>`;
}

function makeTitleDiv(title: string): string {
  return `
<div class="uk-heading-bullet uk-margin-small-top uk-text-bolder" >
${title}
</div>
`;
}

function makeNumberDiv(
  id: string,
  name: string,
  doc: string,
  defaultValue: string,
  placeholder: string
): string {
  return makeParameterDiv(id, "number", name, doc, defaultValue, placeholder);
}

function makeTextDiv(
  id: string,
  name: string,
  doc: string,
  defaultValue: string,
  placeholder: string
): string {
  return makeParameterDiv(id, "text", name, doc, defaultValue, placeholder);
}

function makeParameterDiv(
  id: string,
  type: string,
  name: string,
  doc: string,
  defaultValue: string,
  placeholder: string
): string {
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

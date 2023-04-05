function makeStageDiv(
  id: string,
  inner: string,
  button: string | null
): string {
  const buttonDiv =
    button !== null
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
function makeSettingDiv(id: string, inner: string, button: string): string {
  return makeStageDiv(id, inner, button);
}

function makeDocDiv(id: string, inner: string): string {
  return makeStageDiv(id, inner, null);
}

function makeTitleDiv(title: string): string {
  return `
<div class="uk-heading-bullet uk-margin-small-top uk-text-bolder" >
${title}
</div>
`;
}

function makeNumberParameterDiv(
  id: string,
  name: string,
  doc: string,
  defaultValue: string,
  placeholder: string
): string {
  return makeParameterDiv(id, 'number', name, doc, defaultValue, placeholder);
}

function makeTextParameterDiv(
  id: string,
  name: string,
  doc: string,
  defaultValue: string,
  placeholder: string
): string {
  return makeParameterDiv(id, 'text', name, doc, defaultValue, placeholder);
}

function makeTextDiv(text: string): string {
  return `
<div>
  ${text}
</div>`;
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
function getValueFromElement(id: string): string {
  return (document.getElementById(`select-${id}`) as HTMLInputElement).value;
}

export {
  makeSettingDiv,
  makeDocDiv,
  makeTitleDiv,
  makeNumberParameterDiv,
  makeTextParameterDiv,
  makeTextDiv,
  getValueFromElement,
};

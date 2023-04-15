function makeTitleDiv(title: string): string {
  return `
    <div class="uk-heading-bullet uk-margin-small-top uk-text-bolder" >
    ${title}
    </div>
    `;
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

export { makeTitleDiv, getValueFromElement };

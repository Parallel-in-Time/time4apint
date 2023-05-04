function makeDocDiv(id, inner) {
    return `
<div
    id="${id}"
    class="uk-grid-small uk-child-width-1-1"
    uk-grid
    >
    ${inner}
    <div>
    </div>
</div>`;
}
function makeTextDiv(text) {
    return `
  <div>
    ${text}
  </div>`;
}
export { makeDocDiv, makeTextDiv };

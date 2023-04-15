function makeSettingDiv(id: string, inner: string, button: string): string {
  return `
<div
    id="${id}"
    class="uk-grid-small uk-child-width-1-1"
    uk-grid
    >
      ${inner}
    <div>
      <button
        id="${id}-button"
        class="uk-width-expand uk-button uk-button-default data-callback-button"      
      >${button}
      </button>
    </div>
</div>`;
}

export { makeSettingDiv };

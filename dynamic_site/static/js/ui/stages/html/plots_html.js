function makePlotStageDiv(ids, titles, inner) {
    let tabs = '';
    for (let i = 0; i < ids.length; i++) {
        tabs += makePlotTabTitleDiv(ids[i], titles[i], i == 0);
    }
    return `
<ul id="plot-selection" class="uk-child-width-expand" uk-tab="animation: uk-animation-fade">
  ${tabs}
</ul>
<ul class="uk-switcher">
  ${inner}
</ul>
`;
}
function makePlotTabTitleDiv(id, title, active) {
    return `
  <li class="${active ? 'uk-active' : ''}">
    <a href="#" id="${id}" onclick="setTimeout(() => {window.dispatchEvent(new Event('resize'));}, 150);">${title}</a>
  </li>`;
}
function makePlotTabDiv(id, parameters) {
    return `
<li>
  <div id="${id}">
    <div id="${id}-plot"><div class="uk-section uk-section-muted uk-text-center uk-text-muted">No plot computed</div></div>
    <hr />
    ${makeParameterGridDiv(parameters)}
  </div>
</li>`;
}
function makeParameterGridDiv(inner) {
    return `
<div class="uk-grid-small uk-child-width-1-1" uk-grid>
    ${inner}
</div>
`;
}
export { makePlotTabDiv, makeParameterGridDiv, makePlotStageDiv };

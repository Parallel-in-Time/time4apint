import { Components } from "./components.js";

async function generate(response: object): Promise<void> {
  const components: Components = Object.assign(new Components(), response);
  await components.convertStages();
  console.log(components);

  const [docsDiv, settingsDiv, plotsDiv] = await Promise.all([
    components.generateDocs(),
    components.generateSettings(),
    components.generatePlots(),
  ]);
  console.log(settingsDiv);

  const documentationHTML = document.getElementById("documentation");
  if (documentationHTML !== null) {
    documentationHTML.innerHTML = docsDiv;
  }
  const settingsHTML = document.getElementById("settings");
  if (settingsHTML !== null) {
    settingsHTML.innerHTML = settingsDiv;
  }
  const plotsHTML = document.getElementById("plot");
  if (plotsHTML !== null) {
    plotsHTML.innerHTML = plotsDiv;
  }
}

export { generate };

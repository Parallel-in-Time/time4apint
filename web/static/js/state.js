// --- Utilities ---

function hide(element) {
  element.style.display = "none";
}

function show(element) {
  element.style.display = "block";
}

// --- Constants ---

const stage = {
  "1-A": "1-A",
  "1-B": "1-B",
  2: "2",
};

const firstStageElements = ["N", "tEnd"];
const secondStageElements = ["scheme", "M"];

// --- The State ---

class State {
  constructor(elements) {
    this.elements = elements;
    this.state = stage["1-A"];
    this.firstStageComputed = false;
  }

  update() {
    // Check for 1-A stage elements
    if (!firstStageElements.every((e) => this.elements[e].value !== "")) {
      this.state = stage["1-A"];
      this.firstStageComputed = false; // Reset
      console.log("[x] 1-A\n[ ] 1-B\n[ ] 2");
    }
    // Then check for 1-B stage elements
    else if (!secondStageElements.every((e) => this.elements[e].value !== "")) {
      secondStageElements.forEach((e) =>
        console.log(e, ":", this.elements[e].value)
      );
      this.elements["stage1Button"].disabled = true;

      this.state = stage["1-B"];
      console.log("[x] 1-A\n[x] 1-B\n[ ] 2");
    } else if (!this.firstStageComputed) {
      this.elements["stage1Button"].disabled = false;
      this.state = stage["1-B"];
    }
    // Otherwise we are on stage 2
    else {
      this.state = stage["2"];
      console.log("[x] 1-A\n[x] 1-B\n[x] 2");
    }
    this.updateView();
  }

  updateView() {
    // Display the needed stage elements
    switch (this.state) {
      case "1-A":
        show(this.elements["stage1A"]);
        show(this.elements["stage1ADocumentation"]);
        hide(this.elements["stage1B"]);
        hide(this.elements["stage1BDocumentation"]);
        hide(this.elements["stage2"]);
        hide(this.elements["stage2Documentation"]);
        break;
      case "1-B":
        show(this.elements["stage1A"]);
        show(this.elements["stage1ADocumentation"]);
        show(this.elements["stage1B"]);
        show(this.elements["stage1BDocumentation"]);
        hide(this.elements["stage2"]);
        hide(this.elements["stage2Documentation"]);
        break;
      case "2":
        show(this.elements["stage1A"]);
        show(this.elements["stage1ADocumentation"]);
        show(this.elements["stage1B"]);
        show(this.elements["stage1BDocumentation"]);
        show(this.elements["stage2"]);
        show(this.elements["stage2Documentation"]);
        break;
    }
    const selectionsHeight = this.elements["selections"].clientHeight;
    this.elements["documentation"].style.height = `${selectionsHeight}px`;
  }

  getStageSelections(stage) {
    // (and set the computation state)
    const selections = {};
    // Capture everything with a 'select-' in its tag that is visible
    Array.from(document.querySelectorAll('[id*="select-"]'))
      .filter((elem) => elem.offsetParent !== null) // Remove hidden elements
      .forEach((element) => {
        selections[element.id.replace("select-", "")] = element.value;
      }); // Create object with id: value

    // And add everything with a 'selection-plot'
    Array.from(document.querySelectorAll('[id*="selection-plot"]')).forEach(
      (element) => {
        selections[element.id.replace("selection-plot-", "")] = element.value;
      }
    );

    if (stage === 1) {
      this.firstStageComputed = true;
    }
    this.update();

    // Return it as an object
    return selections;
  }
}

export { State };

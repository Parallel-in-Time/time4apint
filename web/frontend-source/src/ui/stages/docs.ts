import { makeTextDiv, makeDocDiv } from './html/docs_html.js';
import { makeTitleDiv } from './html/common.js';

class DocsStage {
  public title: string;
  public id: string;
  public text: string;
  public dependency: string;
  visible: boolean;

  /**
   * The constructor is empty so that a raw
   * object can be assigned to this class.
   */
  constructor() {
    this.title = '';
    this.id = '';
    this.text = '';
    this.dependency = '';
    this.visible = false;
  }

  /**
   * Initialize the visibility, which depends on whether
   * a dependency is set.
   */
  initializeVisibility(): void {
    this.visible = this.dependency === null || this.dependency === '';
  }

  /**
   * Generate the HTML divs of this stage.
   *
   * @returns The HTML div string.
   */
  async generate(): Promise<string> {
    // TODO: Dependency hook is ignored right now
    const titleDiv = makeTitleDiv(this.title);
    const textDiv = makeTextDiv(this.text);

    // Create the inner html by concatenating the divs
    // and make the complete stage div.
    const inner = `${titleDiv}\n\n${textDiv}`;
    const docDiv = makeDocDiv(this.id, inner);
    return docDiv;
  }
}

export { DocsStage };

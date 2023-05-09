import { useEffect } from 'react';
import { DocsComponentsProps } from './Interfaces';
import ReactMarkdown from 'react-markdown';

function DocsComponent(props: DocsComponentsProps) {
  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    MathJax.typeset();
  }, [props.text]);

  return (
    <>
      <div className='uk-grid-small uk-child-width-1-1' data-uk-grid>
        <div className='uk-heading-bullet uk-margin-small-top uk-text-bolder uk-first-column'>
          {props.title}
        </div>
        <div>
          <ReactMarkdown>{props.text}</ReactMarkdown>
        </div>
      </div>
    </>
  );
}
export default DocsComponent;

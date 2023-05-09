import { useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

function HomeButton() {
  return (
    <div style={{ position: 'absolute', left: '5px', top: '5px' }}>
      <a href='/'>
        <span className='uk-margin-small-right' data-uk-icon='home'></span>
      </a>
    </div>
  );
}

function DocumentationButton(props: { toggleVisibility: Function }) {
  return (
    <div style={{ position: 'absolute', right: '5px', top: '5px' }}>
      <a
        onClick={() => {
          props.toggleVisibility();
        }}
      >
        <span className='uk-margin-small-right' data-uk-icon='info'></span>
      </a>
    </div>
  );
}

function DocumentationModal(props: {
  text: string;
  toggleVisibility: Function;
}) {
  useEffect(() => {
    // @ts-expect-error
    MathJax.typeset();
  }, []);

  return (
    <div
      style={{
        position: 'fixed',
        top: '5%',
        left: '5%',
        right: '5%',
        bottom: '5%',
        zIndex: 10000,
        overflow: 'auto',
        boxShadow: '0 5px 15px rgba(0, 0, 0, 0.08)',
      }}
    >
      <div className='uk-container uk-container-expand uk-background-default  uk-padding-large'>
        <ReactMarkdown>{props.text}</ReactMarkdown>

        <p className='uk-text-right'>
          <button
            className='uk-button uk-button-default uk-modal-close'
            type='button'
            onClick={() => props.toggleVisibility()}
          >
            Close
          </button>
        </p>
      </div>
    </div>
  );
}

export { HomeButton, DocumentationButton, DocumentationModal };

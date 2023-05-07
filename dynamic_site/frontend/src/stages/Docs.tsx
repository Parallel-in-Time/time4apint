import DocsComponent from './DocsComponent';
import { DocsProp } from './Interfaces';

import { useEffect } from 'react';

function Docs(props: DocsProp) {
  // console.log(props.docs);
  const components = props.docs.map((element, i) => (
    <DocsComponent data={element} key={i} />
  ));

  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    MathJax.typeset();
  });

  return (
    <div
      style={{
        overflow: 'auto',
      }}
    >
      <div className='uk-card uk-card-body uk-card-default uk-card-hover'>
        <div className='uk-child uk-child-width-1-1' data-uk-grid>
          {components}
        </div>
      </div>
    </div>
  );
}
export default Docs;

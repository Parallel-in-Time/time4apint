import { useMemo } from 'react';
import { PlotsComponentProp } from './Interfaces';
import Parameter from './parameters/Parameter';

import Plot from 'react-plotly.js';

function PlotsTabComponent(props: {
  data: PlotsComponentProp;
  active: boolean;
}) {
  return (
    <>
      <li className={props.active ? 'uk-active' : ''}>
        <a href='#' id={props.data.id}>
          {props.data.title}
        </a>
      </li>
    </>
  );
}

function PlotsComponent(props: {
  data: PlotsComponentProp;
  updateParameter: Function;
}) {
  const plot = useMemo(() => {
    if (props.data.plot != null) {
      const p = JSON.parse(props.data.plot);
      return <Plot data={p.data} layout={p.layout} />;
    } else {
      return (
        <div>
          <div className='uk-section uk-section-muted uk-text-center uk-text-muted'>
            No plot computed
          </div>
        </div>
      );
    }
  }, []);

  const parameters = // useMemo(() => {
    props.data.parameters.map((element, i) => {
      return (
        <Parameter
          id={element.id}
          name={element.name}
          placeholder={element.placeholder}
          doc={element.doc}
          type={element.type}
          choices={element.choices}
          default={element.default}
          updateParameter={props.updateParameter}
          key={i}
        />
      );
    });
  // }, []); // [props.updateParameter]);
  return (
    <>
      <li>
        <div>
          {plot}
          <hr />
          <div className='uk-grid-small uk-child-width-1-1' data-uk-grid>
            {parameters}
          </div>
        </div>
      </li>
    </>
  );
}

export { PlotsComponent, PlotsTabComponent };

import { useMemo } from 'react';
import { PlotsComponentProp } from './Interfaces';

import Plot from 'react-plotly.js';
import ParameterList from './parameters/ParameterList';

function PlotsTabSelectionComponent(props: {
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
  function makePlot() {
    if (props.data.plot != null) {
      const p = JSON.parse(props.data.plot);
      return (
        <Plot data={p.data} layout={p.layout} config={{ responsive: true }} />
      );
    } else {
      return (
        <div>
          <div className='uk-section uk-section-muted uk-text-center uk-text-muted'>
            No plot computed
          </div>
        </div>
      );
    }
  }
  const plot = useMemo(() => {
    return makePlot();
  }, [props.data]);

  return (
    <>
      <li>
        <div>
          {plot}
          <hr />
          <div className='uk-grid-small uk-child-width-1-1' data-uk-grid>
            <ParameterList
              parameters={props.data.parameters}
              updateParameter={props.updateParameter}
            />
          </div>
        </div>
      </li>
    </>
  );
}

export { PlotsComponent, PlotsTabSelectionComponent };

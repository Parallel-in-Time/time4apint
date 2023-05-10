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
        <a
          href='#'
          id={props.data.id}
          onClick={() => {
            // Resize on tab click to adjust plot size
            window.dispatchEvent(new Event('resize'));
          }}
        >
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
        <Plot
          data={p.data}
          layout={p.layout}
          style={{ width: '100%', height: '100%' }}
          config={{ responsive: true }}
        />
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

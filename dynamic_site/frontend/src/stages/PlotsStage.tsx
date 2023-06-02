import { useMemo } from 'react';
import { PlotsStageProp } from './Interfaces';

import Plot from 'react-plotly.js';

function PlotsStage(props: PlotsStageProp) {
  function makePlot() {
    if (props.plot != null) {
      const p = JSON.parse(props.plot);
      return (
        <Plot
          data={p.data}
          layout={p.layout}
          style={{ width: '100%', minHeight: '20vh' }}
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
  }, [props.plot]);

  return (
    <div>
      <div className='uk-heading-bullet uk-margin-small-top uk-text-bolder'>
        {props.title}
      </div>
      {plot}
      <hr />
    </div>
  );
}

export default PlotsStage;

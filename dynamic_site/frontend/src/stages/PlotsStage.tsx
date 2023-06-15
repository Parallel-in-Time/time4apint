import { useState, useMemo } from 'react';
import { PlotsStageProp } from './Interfaces';

import Plot from 'react-plotly.js';

function PlotModal(props: {
  plot: PlotsStageProp;
  toggleVisibility: Function;
}) {
  const plot = () => {
    if (props.plot.plot != null) {
      const p = JSON.parse(props.plot.plot);
      return (
        <Plot
          data={p.data}
          layout={p.layout}
          style={{ width: '100%', minHeight: '50vh' }}
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
  };

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
      className='uk-container uk-container-expand uk-background-default uk-padding-large'
    >
      <div className='uk-padding-large'>
        <h2 className='uk-title'>{props.plot.title}</h2>

        <div>{plot()}</div>
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

function PlotsStage(props: PlotsStageProp) {
  const [visibleModal, setVisibleModal] = useState(false);

  function toggleVisibility() {
    setVisibleModal((m) => !m);
  }

  function makePlot() {
    if (props.plot != null) {
      const p = JSON.parse(props.plot);
      return (
        <>
          <Plot
            data={p.data}
            layout={p.layout}
            style={{ width: '100%', minHeight: '20vh' }}
            config={{ responsive: true }}
          />

          <button
            className='uk-button uk-button-default uk-width-1-1'
            type='button'
            onClick={() => {
              toggleVisibility();
            }}
          >
            Full screen
          </button>
        </>
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

  const modal = visibleModal ? (
    <PlotModal plot={props} toggleVisibility={toggleVisibility} />
  ) : (
    <></>
  );

  return (
    <>
      <div>{modal}</div>
      <div>
        <div className='uk-heading-bullet uk-margin-small-top uk-text-bolder'>
          {props.title}
        </div>
        {plot}
        <hr />
      </div>
    </>
  );
}

export default PlotsStage;

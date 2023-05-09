import { PlotsComponent, PlotsTabComponent } from './PlotsComponent';

import { PlotsProp } from './Interfaces';

import { useEffect, useMemo } from 'react';

function Plots(props: PlotsProp) {
  const tabComponents = useMemo(
    () =>
      props.plots.map((element, i) => (
        <PlotsTabComponent data={element} active={i === 0} key={i} />
      )),
    [props.computeIndex]
  );
  const innerComponents = useMemo(
    () =>
      props.plots.map((element, i) => (
        <PlotsComponent
          data={element}
          updateParameter={props.updateParameter}
          key={i}
        />
      )),
    [] // [props.computeIndex]
  );

  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    MathJax.typeset();
  });

  return (
    <div className='uk-margin-remove-top' data-uk-grid>
      <div>
        <div className='uk-card uk-card-body uk-card-default uk-card-hover'>
          <div className='uk-child uk-child-width-1-1' data-uk-grid>
            <div className='uk-grid-collapse uk-child-width-1-1' data-uk-grid>
              <ul
                className='uk-child-width-expand'
                data-uk-tab='animation: uk-animation-fade'
              >
                {tabComponents}
              </ul>
              <ul className='uk-switcher'>{innerComponents}</ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Plots;

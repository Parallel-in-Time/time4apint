import SettingsComponent from './SettingsComponent';
import { SettingsProp } from './Interfaces';

import { useEffect } from 'react';

function Settings(props: SettingsProp) {
  const components = props.settings.map((element, i) => (
    <SettingsComponent data={element} key={i} />
  ));

  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    MathJax.typeset();
  });

  return (
    <div data-uk-grid>
      <div>
        <div className='uk-card uk-card-body uk-card-default uk-card-hover'>
          <div className='uk-child uk-child-width-1-1' data-uk-grid>
            <div className='uk-grid-small uk-child-width-1-1' data-uk-grid>
              {components}
            </div>
            <div>
              <button
                className='uk-width-expand uk-button uk-button-default'
                onClick={props.computeCallback}
              >
                Compute
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Settings;

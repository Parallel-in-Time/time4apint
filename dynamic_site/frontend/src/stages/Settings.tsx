import SettingsComponent from './SettingsComponent';
import { SettingsProp } from './Interfaces';

import { useEffect, useMemo } from 'react';

function Settings(props: SettingsProp) {
  const components = useMemo(
    () =>
      props.settings.map((element, i) => (
        <SettingsComponent
          data={element}
          updateParameter={props.updateParameter}
          key={i}
        />
      )),
    [props.settings]
  );

  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    MathJax.typeset();
  }, [components]);

  return (
    <div>
      <div className='uk-card uk-card-body uk-card-default uk-card-hover'>
        <div className='uk-child uk-child-width-1-1' data-uk-grid>
          <div className='uk-grid-small uk-child-width-1-1' data-uk-grid>
            {components}
          </div>
        </div>
      </div>
    </div>
  );
}
export default Settings;

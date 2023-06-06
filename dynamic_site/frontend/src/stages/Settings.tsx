import SettingsStage from './SettingsStage';
import { SettingsProp } from './Interfaces';

import { StageContext } from './StageContext';

import { useEffect, useMemo } from 'react';

function Settings(props: SettingsProp) {
  const components = useMemo(
    () =>
      props.settings.map((element, i) => (
        <StageContext.Provider key={i} value={element.id}>
          <SettingsStage
            title={element.title}
            id={element.id}
            folded={element.folded}
            parameters={element.parameters}
            updateParameter={props.updateParameter}
            key={i}
          />
        </StageContext.Provider>
      )),
    [props.settings]
  );

  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    renderAllMathEquations();
  }, [components]);

  return (
    <div>
      <div className='uk-card uk-card-body uk-card-default uk-card-hover'>
        <div className='uk-child uk-child-width-1-1' data-uk-grid>
          <div className='uk-grid-small uk-child-width-1-1' data-uk-grid>
            <ul uk-accordion='multiple: true'>{components}</ul>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Settings;

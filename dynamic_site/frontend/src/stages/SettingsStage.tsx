import { useMemo } from 'react';
import { SettingsStageProp } from './Interfaces';
import ParameterList from './parameters/ParameterList';

function SettingsStage(props: SettingsStageProp) {
  const parameterList = useMemo(
    () => (
      <ParameterList
        parameters={props.parameters}
        updateParameter={props.updateParameter}
      />
    ),
    [props.parameters]
  );

  return (
    <li className={props.folded ? '' : 'uk-open'}>
      <a className='uk-accordion-title uk-text-default' href='#'>
        <div
          className='uk-heading-bullet uk-margin-small-top uk-text-bolder'
          style={{ color: '#666' }}
        >
          {props.title}
        </div>
      </a>
      <div className='uk-accordion-content'>{parameterList}</div>
    </li>
  );
}
export default SettingsStage;

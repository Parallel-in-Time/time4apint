import { useMemo } from 'react';
import { SettingsComponentProp } from './Interfaces';
import ParameterList from './parameters/ParameterList';

function SettingsComponent(props: {
  data: SettingsComponentProp;
  updateParameter: Function;
}) {
  const parameterList = useMemo(
    () => (
      <ParameterList
        parameters={props.data.parameters}
        updateParameter={props.updateParameter}
      />
    ),
    [props.data]
  );

  return (
    <>
      <div className='uk-heading-bullet uk-margin-small-top uk-text-bolder'>
        {props.data.title}
      </div>

      {parameterList}
    </>
  );
}
export default SettingsComponent;

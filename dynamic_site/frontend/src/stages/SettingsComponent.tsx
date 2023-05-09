import { SettingsComponentProp } from './Interfaces';
import Parameter from './parameters/Parameter';

function SettingsComponent(props: {
  data: SettingsComponentProp;
  updateParameter: Function;
}) {
  const parameters = props.data.parameters.map((element, i) => {
    return (
      <Parameter
        id={element.id}
        name={element.name}
        placeholder={element.placeholder}
        doc={element.doc}
        type={element.type}
        choices={element.choices}
        default={element.default}
        updateParameter={props.updateParameter}
        key={i}
      />
    );
  });

  return (
    <>
      <div className='uk-heading-bullet uk-margin-small-top uk-text-bolder'>
        {props.data.title}
      </div>

      {parameters}
    </>
  );
}
export default SettingsComponent;

import { SettingsComponentProp } from './Interfaces';
import Parameter from './parameters/Parameter';

function SettingsComponent(props: { data: SettingsComponentProp }) {
  const parameters = props.data.parameters.map((element, i) => (
    <Parameter
      unique_id={element.unique_id}
      name={element.name}
      placeholder={element.placeholder}
      doc={element.doc}
      type={element.type}
      choices={element.choices}
      default={element.default}
      key={i}
    />
  ));

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

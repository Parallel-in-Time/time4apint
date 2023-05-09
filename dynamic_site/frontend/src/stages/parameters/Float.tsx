import NumberField from './NumberField';
function checkValidity(v: string) {
  return v !== '' && !isNaN(+v);
}

function Float(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  doc: string;
  updateParameter: Function;
}) {
  return (
    <NumberField
      id={props.id}
      name={props.name}
      defaultValue={props.defaultValue}
      placeholder={props.placeholder}
      doc={props.doc}
      scalar={true}
      updateParameter={props.updateParameter}
      checkValidity={checkValidity}
    />
  );
}

export default Float;

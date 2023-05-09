import NumberField from './NumberField';

function checkValidity(vl: string) {
  const validity = vl
    .split(',')
    .map((v) => v.replace(/\s/g, '') !== '' && !isNaN(+v));
  return validity.every((v) => v === true);
}

function FloatList(props: {
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
      defaultValue={
        Array.isArray(props.defaultValue)
          ? String(props.defaultValue)
          : props.defaultValue
      }
      placeholder={props.placeholder}
      doc={props.doc}
      updateParameter={props.updateParameter}
      scalar={false}
      checkValidity={checkValidity}
    />
  );
}

export default FloatList;

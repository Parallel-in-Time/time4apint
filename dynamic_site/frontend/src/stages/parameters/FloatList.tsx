import { useState } from 'react';
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
  const initialValue = props.defaultValue != null ? props.defaultValue : '';
  const [value, setValue] = useState(initialValue);
  const [valid, setValid] = useState(initialValue !== '');

  const onChangeCallback = (e) => {
    setValue(e.target.value);
    // Valid if not empty, and comma-separated numbers
    const isValid = checkValidity(e.target.value);
    setValid(isValid);
    props.updateParameter({
      id: props.id,
      name: props.name,
      value: isValid ? e.target.value : '',
      isValid: isValid,
    });
  };

  return (
    <input
      uk-tooltip={`title: ${props.doc}`}
      className={`uk-input uk-align-right ${valid ? '' : 'uk-form-danger'}`}
      value={value}
      onChange={onChangeCallback}
      placeholder={props.placeholder}
    />
  );
}

export default FloatList;

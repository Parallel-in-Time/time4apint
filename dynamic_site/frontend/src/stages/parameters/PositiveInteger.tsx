import { useState } from 'react';
function checkValidity(v: string) {
  return v !== '' && !isNaN(+v) && parseInt(v) == v && +v >= 0;
}
function PositiveInteger(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  doc: string;
  updateParameter: Function;
}) {
  const initialValue = props.defaultValue != null ? props.defaultValue : '';
  const [value, setValue] = useState(initialValue);
  const [valid, setValid] = useState(checkValidity(initialValue));

  const onChangeCallback = (e) => {
    setValue(e.target.value);
    // Valid if not empty, a number, and greater or rqual 0
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
      type='number'
      value={value}
      onChange={onChangeCallback}
      placeholder={props.placeholder}
      step='1'
      min='0'
    />
  );
}

export default PositiveInteger;

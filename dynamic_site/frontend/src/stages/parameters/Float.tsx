import { useState } from 'react';

function Float(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  doc: string;
  changeCallback: Function;
}) {
  const [value, setValue] = useState('');
  const [valid, setValid] = useState(false);

  const onChangeCallback = (e) => {
    setValue(e.target.value);
    // Valid if not empty, a number, and greater or equal 0
    const isValid = e.target.value !== '' && !isNaN(+e.target.value);
    setValid(isValid);
    props.changeCallback({
      id: props.id,
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

export default Float;

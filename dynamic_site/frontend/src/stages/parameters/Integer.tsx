import { useState } from 'react';

function Integer(props: {
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
    // Valid if not empty, a number
    const isValid =
      e.target.value !== '' &&
      !isNaN(+e.target.value) &&
      parseInt(e.target.value) == e.target.value;
    setValid(isValid);
    if (isValid) {
      onChangeCallback({ id: props.id, value: value });
    }
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
    />
  );
}

export default Integer;

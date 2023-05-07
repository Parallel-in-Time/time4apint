import { useState } from 'react';

function PositiveInteger(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  doc: string;
}) {
  const [value, setValue] = useState('');
  const [valid, setValid] = useState(false);

  const changeCallback = (e) => {
    setValue(e.target.value);
    // Valid if not empty, a number, and greater or rqual 0
    setValid(
      e.target.value !== '' &&
        !isNaN(+e.target.value) &&
        parseInt(e.target.value) == e.target.value &&
        +e.target.value >= 0
    );
  };

  return (
    <input
      uk-tooltip={`title: ${props.doc}`}
      className={`uk-input uk-align-right ${valid ? '' : 'uk-form-danger'}`}
      type='number'
      value={value}
      onChange={changeCallback}
      placeholder={props.placeholder}
      step='1'
      min='0'
    />
  );
}

export default PositiveInteger;

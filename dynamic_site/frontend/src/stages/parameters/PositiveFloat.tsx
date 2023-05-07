import { useState } from 'react';

function PositiveFloat(props: {
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
    // Valid if not empty, a number, and greater or equal 0
    setValid(
      e.target.value !== '' && !isNaN(+e.target.value) && +e.target.value >= 0
    );
  };

  return (
    <input
      uk-tooltip={`title: ${props.doc}`}
      className={`uk-input uk-align-right ${valid ? '' : 'uk-form-danger'}`}
      value={value}
      onChange={changeCallback}
      placeholder={props.placeholder}
    />
  );
}

export default PositiveFloat;

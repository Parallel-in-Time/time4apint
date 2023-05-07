import { useState } from 'react';

function FloatList(props: {
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
    // Valid if not empty, and comma-separated numbers
    const validity = e.target.value
      .split(',')
      .map((v) => v.replace(/\s/g, '') !== '' && !isNaN(+v));
    setValid(validity.every((v) => v === true));
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

export default FloatList;

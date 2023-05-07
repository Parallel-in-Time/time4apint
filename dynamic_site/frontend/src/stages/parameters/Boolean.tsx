import { useState } from 'react';

function Boolean(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  doc: string;
}) {
  const [value, setValue] = useState('');
  const changeCallback = (e) => {
    setValue(e.target.value);
  };

  return (
    <input
      uk-tooltip={`title: ${props.doc}`}
      className={`uk-checkbox uk-align-right`}
      value={value}
      onChange={changeCallback}
      placeholder={props.placeholder}
      type='checkbox'
    />
  );
}

export default Boolean;

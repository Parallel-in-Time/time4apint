import { useState } from 'react';

function Boolean(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  doc: string;
  updateParameter: Function;
}) {
  const initialValue = props.defaultValue != null ? props.defaultValue : '';
  const [value, setValue] = useState(initialValue);

  function onChangeCallback(e) {
    setValue(e.target.value);
    props.updateParameter({
      id: props.id,
      name: props.name,
      value: e.target.value,
      isValid: true,
    });
  }
  // console.log(props.updateParameter);

  return (
    <input
      uk-tooltip={`title: ${props.doc}`}
      className={`uk-checkbox uk-align-right`}
      value={value}
      onChange={onChangeCallback}
      placeholder={props.placeholder}
      type='checkbox'
    />
  );
}

export default Boolean;

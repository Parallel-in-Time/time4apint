import { useEffect, useState } from 'react';

function Boolean(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  doc: string;
  updateParameter: Function;
}) {
  const initialValue = props.defaultValue != null ? props.defaultValue : false;
  const [value, setValue] = useState(initialValue);

  const onChangeCallback = (v: string) => {
    setValue(v);
    props.updateParameter({
      id: props.id,
      name: props.name,
      value: v,
      isValid: true,
    });
  };

  useEffect(() => onChangeCallback(String(initialValue)), []);

  return (
    <input
      uk-tooltip={`title: ${props.doc}`}
      className={`uk-checkbox uk-align-right`}
      value={String(value)}
      onChange={(e) => onChangeCallback(e.target.value)}
      placeholder={props.placeholder}
      type='checkbox'
    />
  );
}

export default Boolean;

import { useEffect, useState } from 'react';

function Enumeration(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  choices: Array<string>;
  doc: string;
  updateParameter: Function;
}) {
  const initialValue = props.defaultValue == null ? '' : props.defaultValue;
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

  useEffect(() => onChangeCallback(initialValue), []);

  const options = props.choices.map((choice, i) => {
    return (
      <option value={choice} key={i}>
        {choice}
      </option>
    );
  });

  return (
    <select
      id={`select-${props.id}`}
      className='uk-select'
      onChange={(e) => onChangeCallback(e.target.value)}
      data-uk-tooltip={`title: ${props.doc}`}
      value={value}
    >
      {options}
    </select>
  );
}

export default Enumeration;

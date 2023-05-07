import { useState } from 'react';

function Enumeration(props: {
  id: string;
  name: string;
  defaultValue: string;
  placeholder: string;
  choices: Array<string>;
  doc: string;
}) {
  const initialValue = props.defaultValue == null ? '' : props.defaultValue;
  const [value, setValue] = useState(initialValue);

  const changeCallback = (e) => {
    setValue(e.target.value);
  };

  const options = props.choices.map((choice, i) => {
    // if (props.defaultValue === choice) {
    //   return (
    //     <option selected={true} value={choice} key={i}>
    //       {choice}
    //     </option>
    //   );
    // }
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
      onChange={changeCallback}
      data-uk-tooltip={`title: ${props.doc}`}
      value={value}
    >
      {options}
    </select>
  );
}

export default Enumeration;

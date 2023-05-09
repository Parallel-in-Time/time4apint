import { useEffect, useMemo } from 'react';
import { Error } from './Info';

interface ParameterValue {
  id: string;
  value: string;
  isValid: boolean;
}

function InfoBar(props: { [id: string]: ParameterValue; updateFlag: number }) {
  const messages = useMemo(() => {
    console.log('running', props.updateFlag);
    const errorKeys = Object.keys(props.parameters).filter(
      (k) => !props.parameters[k].isValid
    );

    return errorKeys.map((k, i) => {
      return (
        <Error message={`${props.parameters[k].name} is missing`} key={i} />
      );
    });
  }, []); // [props.updateFlag]);

  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    MathJax.typeset();
  });

  return (
    <div className='uk-width-1-1' data-uk-sticky>
      <div
        className='uk-grid-small uk-section uk-section-muted uk-padding-small'
        data-uk-grid
      >
        {messages}
      </div>
    </div>
  );
}
export default InfoBar;

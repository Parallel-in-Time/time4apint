import { useEffect, useMemo } from 'react';

function Error(props: { name: string }) {
  const errorTextStyle = {
    fontWeight: 'bold',
  };
  return (
    <div className='uk-alert-danger uk-margin-small-right' data-uk-alert>
      <p>
        <span style={errorTextStyle}>{props.name}</span> is missing.
      </p>
    </div>
  );
}

function InfoBar(props: {
  invalidParameters: Array<string>;
  computeCallback: Function;
}) {
  // console.log(props.invalidParameters);
  function makeBar() {
    if (props.invalidParameters.length == 0) {
      // If there are no invalid parameters
      return (
        <button
          className='uk-width-expand uk-button uk-button-large uk-button-primary'
          onClick={() => props.computeCallback()}
        >
          Compute
        </button>
      );
    } else {
      // Otherwise return error messages
      return props.invalidParameters.map((name, i) => (
        <Error name={name} key={i} />
      ));
    }
  }

  const bar = useMemo(() => makeBar(), [props.invalidParameters]);

  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    MathJax.typeset();
  }, [bar]);

  return (
    <div className='uk-width-1-1' data-uk-sticky>
      <div
        className='uk-grid-small uk-section uk-section-muted uk-padding-small uk-padding-remove-right'
        data-uk-grid
      >
        {bar}
      </div>
    </div>
  );
}
export default InfoBar;

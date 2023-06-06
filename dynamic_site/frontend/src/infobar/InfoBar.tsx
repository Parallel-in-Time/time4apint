import { useEffect, useMemo } from 'react';

interface Parameters {
  [stage: string]: {
    [id: string]: {
      id: string;
      name: string;
      value: string;
      isValid: boolean;
      stage: string;
    };
  };
}

function Error(props: { name: string }) {
  return (
    <div className='uk-alert-danger uk-margin-small-right' data-uk-alert>
      <p className='uk-text-bold'>{props.name}</p>
    </div>
  );
}

function Info(props: { message: string }) {
  return (
    <div className='uk-alert-success' data-uk-alert>
      <p>{props.message}</p>
    </div>
  );
}

function InfoBar(props: {
  invalidParameters: Array<string>;
  parameters: Parameters;
  computeCallback: Function;
}) {
  const computeButton = useMemo(
    () => (
      <button
        className='uk-width-expand uk-button uk-button-large uk-button-primary'
        onClick={() => props.computeCallback()}
        disabled={props.invalidParameters.length !== 0}
      >
        Compute
      </button>
    ),
    [props.invalidParameters, props.parameters]
  );

  const errors = useMemo(() => {
    if (props.invalidParameters.length === 0) {
      return <Info message='All required parameters set.' />;
    }

    return props.invalidParameters.map((name, i) => (
      <Error name={name} key={i} />
    ));
  }, [props.invalidParameters]);

  useEffect(() => {
    // On new render, check for new math formulas
    // @ts-expect-error
    renderAllMathEquations();
  }, [errors]);

  return (
    <div className='uk-width-1-1' data-uk-sticky>
      <div
        className='uk-grid-small uk-section uk-section-muted uk-padding-small'
        data-uk-grid
      >
        <div className='uk-width-expand' data-uk-grid>
          {errors}
        </div>
        <div className='uk-width-1-4'>{computeButton}</div>
      </div>
    </div>
  );
}
export default InfoBar;

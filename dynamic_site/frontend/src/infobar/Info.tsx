function Info(props: { message: string }) {
  return (
    <div className='uk-alert-success uk-margin-small-right' data-uk-alert>
      <a className='uk-alert-close' data-uk-close></a>

      <p>{props.message}</p>
    </div>
  );
}

function Warning(props: { message: string }) {
  return (
    <div className='uk-alert-warning uk-margin-small-right' data-uk-alert>
      <p>{props.message}</p>
    </div>
  );
}

function Error(props: { message: string }) {
  return (
    <div className='uk-alert-danger uk-margin-small-right' data-uk-alert>
      <p>{props.message}</p>
    </div>
  );
}
export { Info, Warning, Error };

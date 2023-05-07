import { Info, Warning, Error } from './Info';

function InfoBar() {
  return (
    <div className='uk-width-1-1' data-uk-sticky>
      <div
        className='uk-grid-small uk-section uk-section-muted uk-padding-small'
        data-uk-grid
      >
        <Info message='Everything is fine' />
        <Warning message='`\lambda is missing`' />
        <Error message='tEnd is not okay' />
      </div>
    </div>
  );
}
export default InfoBar;

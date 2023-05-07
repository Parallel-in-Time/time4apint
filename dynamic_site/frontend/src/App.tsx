import '../node_modules/uikit/dist/css/uikit.css';
import '../node_modules/uikit/dist/js/uikit.min';

import Stages from './stages/Stages';
import InfoBar from './infobar/InfoBar';

function Title(props: { title: string }) {
  return (
    <div className='uk-width-1-1'>
      <h1 className='uk-heading uk-heading-line uk-text-center'>
        <span> {props.title} </span>
      </h1>
    </div>
  );
}

function App() {
  return (
    <div className='uk-height-1-1 uk-padding uk-background-muted'>
      <div className='uk-container uk-container-expand'>
        <Title title='Hello App' />

        <InfoBar />

        <Stages />
      </div>
    </div>
  );
}

export default App;

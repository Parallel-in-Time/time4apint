import { PlotsComponentProp } from './Interfaces';
import Parameter from './parameters/Parameter';

function PlotsTabComponent(props: {
  data: PlotsComponentProp;
  active: boolean;
}) {
  return (
    <>
      <li className={props.active ? 'uk-active' : ''}>
        <a href='#' id={props.data.id}>
          {props.data.title}
        </a>
      </li>
    </>
  );
}

function PlotsComponent(props: {
  data: PlotsComponentProp;
  parameterCallback: Function;
}) {
  const parameters = props.data.parameters.map((element, i) => (
    <Parameter
      id={element.id}
      name={element.name}
      placeholder={element.placeholder}
      doc={element.doc}
      type={element.type}
      choices={element.choices}
      default={element.default}
      changeCallback={props.parameterCallback}
      key={i}
    />
  ));
  return (
    <>
      <li>
        <div>
          <div id={`plot-${props.data.id}`}>
            <div className='uk-section uk-section-muted uk-text-center uk-text-muted'>
              No plot computed
            </div>
          </div>
          <hr />
          <div className='uk-grid-small uk-child-width-1-1' data-uk-grid>
            {parameters}
          </div>
        </div>
      </li>
    </>
  );
}

export { PlotsComponent, PlotsTabComponent };

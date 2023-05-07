import { ParameterProp, ParameterType } from '../Interfaces';

import StrictlyPositiveInteger from './StrictlyPositiveInteger';
import Integer from './Integer';
import PositiveInteger from './PositiveInteger';
import PositiveFloat from './PositiveFloat';
import Float from './Float';
import Enumeration from './Enumeration';
import FloatList from './FloatList';
import Boolean from './Boolean';

function Parameter(prop: ParameterProp) {
  function getParameterType() {
    switch (prop.type) {
      case ParameterType.Integer:
        return (
          <Integer
            id={prop.id}
            name={prop.name}
            defaultValue={prop.default}
            placeholder={prop.placeholder}
            doc={prop.doc}
            changeCallback={prop.changeCallback}
          />
        );
      case ParameterType.PositiveInteger:
        return (
          <PositiveInteger
            id={prop.id}
            name={prop.name}
            defaultValue={prop.default}
            placeholder={prop.placeholder}
            doc={prop.doc}
          />
        );
      case ParameterType.StrictlyPositiveInteger:
        return (
          <StrictlyPositiveInteger
            id={prop.id}
            name={prop.name}
            defaultValue={prop.default}
            placeholder={prop.placeholder}
            doc={prop.doc}
          />
        );
      case ParameterType.PositiveFloat:
        return (
          <PositiveFloat
            id={prop.id}
            name={prop.name}
            defaultValue={prop.default}
            placeholder={prop.placeholder}
            doc={prop.doc}
          />
        );
      case ParameterType.Float:
        return (
          <Float
            id={prop.id}
            name={prop.name}
            defaultValue={prop.default}
            placeholder={prop.placeholder}
            doc={prop.doc}
            changeCallback={prop.changeCallback}
          />
        );
      case ParameterType.Enumeration:
        return (
          <Enumeration
            id={prop.id}
            name={prop.name}
            defaultValue={prop.default}
            placeholder={prop.placeholder}
            choices={prop.choices}
            doc={prop.doc}
          />
        );
      case ParameterType.FloatList:
        return (
          <FloatList
            id={prop.id}
            name={prop.name}
            defaultValue={prop.default}
            placeholder={prop.placeholder}
            doc={prop.doc}
          />
        );
      case ParameterType.Boolean:
        return (
          <Boolean
            id={prop.id}
            name={prop.name}
            defaultValue={prop.default}
            placeholder={prop.placeholder}
            doc={prop.doc}
          />
        );
      default:
        console.log('nope, nope, nope, the parameter type is unkown.');
        return <div>Unknown parameter</div>;
    }
  }

  return (
    <div className='uk-margin-small-left uk-padding-small-left' data-uk-grid>
      <span className='uk-padding-remove-left uk-margin-small-right uk-margin-small-top'>
        {prop.name}
      </span>

      <div className='uk-width-expand@m uk-padding-remove-left'>
        {getParameterType()}
      </div>
    </div>
  );
}

export default Parameter;

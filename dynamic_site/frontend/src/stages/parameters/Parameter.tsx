import { ParameterProp, ParameterType } from '../Interfaces';

import StrictlyPositiveInteger from './StrictlyPositiveInteger';
import Integer from './Integer';
import PositiveInteger from './PositiveInteger';
import PositiveFloat from './PositiveFloat';
import Float from './Float';
import Enumeration from './Enumeration';
import FloatList from './FloatList';
import Boolean from './Boolean';
import { useMemo } from 'react';

function Parameter(props: ParameterProp) {
  function getParameterType() {
    switch (props.type) {
      case ParameterType.Integer:
        return (
          <Integer
            id={props.id}
            name={props.name}
            defaultValue={props.default}
            placeholder={props.placeholder}
            doc={props.doc}
            updateParameter={props.updateParameter}
          />
        );
      case ParameterType.PositiveInteger:
        return (
          <PositiveInteger
            id={props.id}
            name={props.name}
            defaultValue={props.default}
            placeholder={props.placeholder}
            doc={props.doc}
            updateParameter={props.updateParameter}
          />
        );
      case ParameterType.StrictlyPositiveInteger:
        return (
          <StrictlyPositiveInteger
            id={props.id}
            name={props.name}
            defaultValue={props.default}
            placeholder={props.placeholder}
            doc={props.doc}
            updateParameter={props.updateParameter}
          />
        );
      case ParameterType.PositiveFloat:
        return (
          <PositiveFloat
            id={props.id}
            name={props.name}
            defaultValue={props.default}
            placeholder={props.placeholder}
            doc={props.doc}
            updateParameter={props.updateParameter}
          />
        );
      case ParameterType.Float:
        return (
          <Float
            id={props.id}
            name={props.name}
            defaultValue={props.default}
            placeholder={props.placeholder}
            doc={props.doc}
            updateParameter={props.updateParameter}
          />
        );
      case ParameterType.Enumeration:
        return (
          <Enumeration
            id={props.id}
            name={props.name}
            defaultValue={props.default}
            placeholder={props.placeholder}
            choices={props.choices}
            doc={props.doc}
            updateParameter={props.updateParameter}
          />
        );
      case ParameterType.FloatList:
        return (
          <FloatList
            id={props.id}
            name={props.name}
            defaultValue={props.default}
            placeholder={props.placeholder}
            doc={props.doc}
            updateParameter={props.updateParameter}
          />
        );
      case ParameterType.Boolean:
        return (
          <Boolean
            id={props.id}
            name={props.name}
            defaultValue={props.default}
            placeholder={props.placeholder}
            doc={props.doc}
            updateParameter={props.updateParameter}
          />
        );
      default:
        console.log('nope, nope, nope, the parameter type is unkown.');
        return <div>Unknown parameter</div>;
    }
  }

  const parameter = useMemo(() => getParameterType(), []);

  return (
    <div className='uk-margin-small-left uk-padding-small-left' data-uk-grid>
      <span className='uk-padding-remove-left uk-margin-small-right uk-margin-small-top'>
        {props.name}
      </span>

      <div className='uk-width-expand@m uk-padding-remove-left'>
        {parameter}
      </div>
    </div>
  );
}

export default Parameter;

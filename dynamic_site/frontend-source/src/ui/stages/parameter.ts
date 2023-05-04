import {
  makeIntegerParameterDiv,
  makePositiveIntegerParameterDiv,
  makeStrictlyPositiveIntegerParameterDiv,
  makePositiveFloatParameterDiv,
  makeFloatParameterDiv,
  makeEnumerationParameterDiv,
  makeFloatListParameterDiv,
  makeBooleanParameterDiv,
} from './html/parameter_html.js';

enum ParameterType {
  Integer = 'Integer',
  PositiveInteger = 'PositiveInteger',
  StrictlyPositiveInteger = 'StrictlyPositiveInteger',
  PositiveFloat = 'PositiveFloat',
  Float = 'Float',
  FloatList = 'FloatList',
  Enumeration = 'Enumeration',
  Boolean = 'Boolean',
}

function getParameterTypeId(type: ParameterType): string {
  return (
    type[0].toLowerCase() +
    type
      .slice(1, type.length)
      .replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)
  );
}

type Parameter = {
  id: string;
  name: string;
  placeholder: string;
  doc: string;
  type: ParameterType;
  choices: null | Array<string>;
  default: null | string | boolean | number;
};

function makeParameterHTML(param: Parameter): string {
  const id = param.id;
  const name = param.name;
  const doc = param.doc;
  const defaultValue = param.default === null ? '' : String(param.default);
  const placeholder = param.placeholder;

  switch (param.type) {
    case ParameterType.Integer:
      return makeIntegerParameterDiv(id, name, doc, defaultValue, placeholder);

    case ParameterType.PositiveInteger:
      return makePositiveIntegerParameterDiv(
        id,
        name,
        doc,
        defaultValue,
        placeholder
      );

    case ParameterType.StrictlyPositiveInteger:
      return makeStrictlyPositiveIntegerParameterDiv(
        id,
        name,
        doc,
        defaultValue,
        placeholder
      );

    case ParameterType.PositiveFloat:
      return makePositiveFloatParameterDiv(
        id,
        name,
        doc,
        defaultValue,
        placeholder
      );

    case ParameterType.Float:
      return makeFloatParameterDiv(id, name, doc, defaultValue, placeholder);

    case ParameterType.FloatList:
      return makeFloatListParameterDiv(
        id,
        name,
        doc,
        defaultValue,
        placeholder
      );

    case ParameterType.Enumeration:
      return makeEnumerationParameterDiv(
        id,
        name,
        doc,
        param.choices ?? [],
        defaultValue
      );

    case ParameterType.Boolean:
      makeBooleanParameterDiv(id, name, doc, defaultValue === 'true');

    default:
      console.error(
        `ERROR: ${param.type} did not occur in the the switch case`
      );
      return 'error';
  }
}

async function setInputOnChangeCallback(
  className: string,
  fn: Function
): Promise<void> {
  const inputs = document.getElementsByClassName(className);
  for (let i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener('change', (event) => {
      if (event.target instanceof HTMLElement) {
        fn(event.target);
      }
    });
  }
}

/**
 * Set the input callback that check onchange
 * of any of the set inputs whether they are valid,
 * i.e., strictly positive etc.
 */
async function setInputOnChangeCallbacks(): Promise<void> {
  const addClass = (target: HTMLInputElement) => {
    target.classList.add('uk-form-danger');
  };
  const removeClass = (target: HTMLInputElement) => {
    target.classList.remove('uk-form-danger');
  };

  // Integer
  setInputOnChangeCallback(
    getParameterTypeId(ParameterType.Integer),
    (target: HTMLInputElement) => {
      removeClass(target);
    }
  );

  // PositiveInteger
  setInputOnChangeCallback(
    getParameterTypeId(ParameterType.PositiveInteger),
    (target: HTMLInputElement) => {
      if (+target.value < 0) {
        addClass(target);
      } else {
        removeClass(target);
      }
    }
  );

  // StrictlyPositiveInteger
  setInputOnChangeCallback(
    getParameterTypeId(ParameterType.StrictlyPositiveInteger),
    (target: HTMLInputElement) => {
      if (+target.value <= 0) {
        addClass(target);
      } else {
        removeClass(target);
      }
    }
  );

  // PositiveFloat
  setInputOnChangeCallback(
    getParameterTypeId(ParameterType.PositiveFloat),
    (target: HTMLInputElement) => {
      if (+target.value < 0) {
        addClass(target);
      } else {
        removeClass(target);
      }
    }
  );

  // Float
  setInputOnChangeCallback(
    getParameterTypeId(ParameterType.Float),
    (target: HTMLInputElement) => {
      removeClass(target);
    }
  );

  // FloatList
  setInputOnChangeCallback(
    getParameterTypeId(ParameterType.FloatList),
    (target: HTMLInputElement) => {
      // TODO: Check with a regex, whether this is a list of floats!
      removeClass(target);
    }
  );

  // Enumeration
  setInputOnChangeCallback(
    getParameterTypeId(ParameterType.Enumeration),
    (_: HTMLInputElement) => {}
  );

  // Boolean
  setInputOnChangeCallback(
    getParameterTypeId(ParameterType.Boolean),
    (_: HTMLInputElement) => {}
  );
}

export {
  Parameter,
  ParameterType,
  getParameterTypeId,
  makeParameterHTML,
  setInputOnChangeCallbacks,
};

enum ParameterType {
  Integer,
  PositiveInteger,
  StrictlyPositiveInteger,
  PositiveFloat,
  Float,
  Enumeration,
  FloatList,
  Boolean,
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

export { Parameter, ParameterType };

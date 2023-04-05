enum ParameterType {
  PositiveInteger,
  StrictlyPositiveInteger,
  PositiveFloat,
  Float,
  Enumeration,
  FloatList,
  Boolean,
}

type Parameter = {
  name: string;
  id: string;
  values: string;
  doc: string;
  type: ParameterType;
  choices: null | Array<string>;
  default: null | string | boolean | number;
};

export { Parameter, ParameterType };

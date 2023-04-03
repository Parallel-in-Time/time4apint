enum ParameterType {
  PositiveInteger,
  StrictlyPositiveInteger,
  PositiveFloat,
  Float,
  Enumeration,
  FloatList,
  Boolean,
}

class SettingsStage {
  constructor(
    public title: string,
    public id: string,
    public parameterType: ParameterType,
    public dependency: string
  ) {}

  buildUI() {
    console.log('Generating UI...');
  }
}

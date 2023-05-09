export interface DocsComponentsProps {
  title: string;
  id: string;
  text: string;
  activated: boolean;
  dependency: string;
}

export interface DocsProp {
  docs: Array<DocsComponentsProps>;
}

export interface SettingsComponentProp {
  title: string;
  id: string;
  activated: boolean;
  dependency: string;
  parameters: Array<ParameterProp>;
}

export interface SettingsProp {
  settings: Array<SettingsComponentProp>;
  updateParameter: Function;
  computeCallback: Function;
  computeIndex: number;
}

export interface PlotsComponentProp {
  title: string;
  id: string;
  activated: boolean;
  dependency: string;
  plot: string;
  parameters: Array<ParameterProp>;
}

export interface PlotsProp {
  plots: Array<PlotsComponentProp>;
  updateParameter: Function;
  computeIndex: number;
}

export interface ParameterProp {
  id: string;
  name: string;
  placeholder: string;
  doc: string;
  type: ParameterType;
  choices: Array<string>;
  default: string;
  updateParameter: Function;
}

export enum ParameterType {
  Integer = 'Integer',
  PositiveInteger = 'PositiveInteger',
  StrictlyPositiveInteger = 'StrictlyPositiveInteger',
  PositiveFloat = 'PositiveFloat',
  Float = 'Float',
  Enumeration = 'Enumeration',
  FloatList = 'FloatList',
  Boolean = 'Boolean',
}

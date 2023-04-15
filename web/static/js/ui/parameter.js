var ParameterType;
(function (ParameterType) {
    ParameterType[ParameterType["Integer"] = 0] = "Integer";
    ParameterType[ParameterType["PositiveInteger"] = 1] = "PositiveInteger";
    ParameterType[ParameterType["StrictlyPositiveInteger"] = 2] = "StrictlyPositiveInteger";
    ParameterType[ParameterType["PositiveFloat"] = 3] = "PositiveFloat";
    ParameterType[ParameterType["Float"] = 4] = "Float";
    ParameterType[ParameterType["Enumeration"] = 5] = "Enumeration";
    ParameterType[ParameterType["FloatList"] = 6] = "FloatList";
    ParameterType[ParameterType["Boolean"] = 7] = "Boolean";
})(ParameterType || (ParameterType = {}));
export { ParameterType };

"use strict";
var ParameterType;
(function (ParameterType) {
    ParameterType[ParameterType["PositiveInteger"] = 0] = "PositiveInteger";
    ParameterType[ParameterType["StrictlyPositiveInteger"] = 1] = "StrictlyPositiveInteger";
    ParameterType[ParameterType["PositiveFloat"] = 2] = "PositiveFloat";
    ParameterType[ParameterType["Float"] = 3] = "Float";
    ParameterType[ParameterType["Enumeration"] = 4] = "Enumeration";
    ParameterType[ParameterType["FloatList"] = 5] = "FloatList";
    ParameterType[ParameterType["Boolean"] = 6] = "Boolean";
})(ParameterType || (ParameterType = {}));
class SettingsStage {
    constructor(title, id, parameterType, dependency) {
        Object.defineProperty(this, "title", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: title
        });
        Object.defineProperty(this, "id", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: id
        });
        Object.defineProperty(this, "parameterType", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: parameterType
        });
        Object.defineProperty(this, "dependency", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: dependency
        });
    }
    buildUI() {
        console.log('Generating UI...');
    }
}

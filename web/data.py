from blockops.schemes import SCHEMES
from blockops.utils.params import Parameter, MultipleChoices
from blockops.problem import BlockProblem

from typing import Any

# API definitions

types = [
    'PositiveInteger',
    'StrictlyPositiveInteger',
    'PositiveFloat',
    'Float',
    'Enumeration',
    'FloatList',
    'Boolean',
]

# webutils


def convert_to_web(param: Parameter) -> str | list[str]:
    web_type = convert_to_web_inner(param)
    if len(web_type) == 1:
        return web_type[0]
    return web_type


def convert_to_web_inner(param: Parameter) -> list[str]:
    from blockops.utils.params import PositiveInteger, ScalarNumber, VectorNumbers, MultipleChoices, CustomPoints, Boolean
    if isinstance(param, PositiveInteger):
        if param.strict:
            return ['StrictlyPositiveInteger']
        return ['PositiveInteger']
    if isinstance(param, ScalarNumber):
        if param.positive:
            return ['PositiveFloat']
        return ['Float']
    if isinstance(param, VectorNumbers) or isinstance(param, CustomPoints):
        return ['FloatList']
    if isinstance(param, Boolean):
        return ['Boolean']
    if isinstance(param, MultipleChoices):
        if len(param.pTypes) > 0:
            return ['Enumeration'] + [
                convert_to_web_inner(paramType)[0]
                for paramType in param.pTypes
            ]
        return ['Enumeration']
    return ['Unknown']


# data


class SettingsStage:

    def __init__(self, title: str, unique_name: str,
                 parameters: dict[str,
                                  Parameter], dependency: str | None) -> None:
        self.title: str = title
        self.unique_name: str = unique_name
        self.parameters: dict[str, Parameter] = parameters
        self.dependency: str | None = dependency

    def serialize(
        self
    ) -> dict[str, Any]:  # Returns a dictionary to be sent to the frontend
        result = {}
        for name, parameter in self.parameters.items():
            web_type = convert_to_web(parameter)
            choices = None
            if isinstance(parameter, MultipleChoices):
                choices = parameter.choices
            result[name] = {
                'values': parameter.__doc__,
                'doc': parameter.docs,
                'type': web_type,
                'choices': choices,  # None, if thats the only one
                'default': parameter.default,  # None if not optional
            }
        result['title'] = self.title
        result['id'] = self.unique_name
        result['dependency'] = self.dependency
        return result


stage_1_block_problem = SettingsStage('Definition of a Block Problem', 'S1',
                                      BlockProblem.PARAMS, None)

# Second stage will be created dynamically, when the results of the first stage are sent back
# settings_stage_2_block_scheme = SettingStage('S2', BlockProblem.PARAMS, 'S1')

documentation = {'abc': 'text'}

import json

print(json.dumps(stage_1_block_problem.serialize(), indent=4))
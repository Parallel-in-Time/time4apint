from blockops.utils.params import Parameter, MultipleChoices

from typing import Any

from web.utils import slugify

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


class DocsStage:

    def __init__(
        self,
        unique_name: str,
        title: str,
        text: str,
        dependency: str | None,
    ) -> None:
        self.unique_name: str = unique_name
        self.title: str = title
        self.text: str = text
        self.dependency: str | None = dependency

    def serialize(self) -> dict[str, Any]:
        return {
            'title': self.title,
            'text': self.text,
            'dependency': self.dependency,
        }


class SettingsStage:

    def __init__(
        self,
        unique_name: str,
        title: str,
        parameters: dict[str, Parameter],
        button_name: str,
        dependency: str | None,
    ) -> None:
        self.title: str = title
        self.unique_name: str = unique_name
        self.parameters: dict[str, Parameter] = parameters
        self.button: str = button_name
        self.dependency: str | None = dependency

    def serialize(
        self
    ) -> dict[str, Any]:  # Returns a dictionary to be sent to the frontend
        result: dict[str, Any] = {'parameters': []}
        for name, parameter in self.parameters.items():
            web_type = convert_to_web(parameter)
            choices = None
            if isinstance(parameter, MultipleChoices):
                choices = parameter.choices
            doc = parameter.docs
            if isinstance(doc, str):
                doc = doc.replace(':math:', '')
            result['parameters'].append({
                'name': name,
                'id': slugify(name),
                'values': parameter.__doc__,
                'doc': doc,
                'type': web_type,
                'choices': choices,  # None, if thats the only one
                'default': parameter.default,  # None if not optional
            })
        result['title'] = self.title
        result['id'] = self.unique_name
        result['button'] = self.button
        result['dependency'] = self.dependency
        return result

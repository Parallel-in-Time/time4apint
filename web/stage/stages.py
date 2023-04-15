# from blockops.utils.params import Parameter, MultipleChoices

from typing import Any

from web.stage.utils import slugify
from web.stage.parameters import Parameter
# TODO: Integrate the stage parameters and replace the blockops params


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
        parameters: list[Parameter],
        button_name: str,
        dependency: str | None,
    ) -> None:
        self.title: str = title
        self.unique_name: str = unique_name
        self.parameters: list[Parameter] = parameters
        self.button: str = button_name
        self.dependency: str | None = dependency

    def serialize(
        self
    ) -> dict[str, Any]:  # Returns a dictionary to be sent to the frontend
        return {
            'title': self.title,
            'id': self.unique_name,
            'button': self.button,
            'dependency': self.dependency,
            'parameters':
            [parameter.serialize() for parameter in self.parameters],
        }


class PlotsStage:

    def __init__(
        self,
        unique_name: str,
        title: str,
        parameters: list[Parameter],
        plot: Any | None,
        dependency: str | None,
    ) -> None:
        self.title: str = title
        self.unique_name: str = unique_name
        self.parameters: list[Parameter] = parameters
        self.plot: Any | None = plot
        self.dependency: str | None = dependency

    def serialize(self) -> dict[str, Any]:
        return {
            'title': self.title,
            'id': self.unique_name,
            'plot': self.plot,
            'dependency': self.dependency,
            'parameters':
            [parameter.serialize() for parameter in self.parameters],
        }

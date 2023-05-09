from copy import deepcopy
from typing import Any

from dynamic_site.stage.parameters import Parameter

import mistune


class DocsStage:

    def __init__(
        self,
        unique_name: str,
        title: str,
        text: str,
        activated: bool,
        dependency: str | None,
        md_to_html: bool = False,
    ) -> None:
        self.unique_name: str = unique_name
        self.title: str = title
        self.text: str = text
        if md_to_html:
            self.text = str(mistune.create_markdown(plugins=['math'])(text))
        self.activated: bool = activated
        self.dependency: str | None = dependency

    def copy(self):
        """Returns a new DocsStage but as a copy.

        Returns:
            DocsStage. A new docs stage.
        """
        return DocsStage(
            self.unique_name,
            self.title,
            self.text,
            self.activated,
            self.dependency,
        )

    def serialize(self) -> dict[str, Any]:
        return {
            'id': self.unique_name,
            'title': self.title,
            'text': self.text,
            'activated': self.activated,
            'dependency': self.dependency,
        }


class SettingsStage:

    def __init__(
        self,
        unique_name: str,
        title: str,
        parameters: list[Parameter],
        activated: bool,
        dependency: str | None,
    ) -> None:
        self.unique_name: str = unique_name
        self.title: str = title
        self.parameters: list[Parameter] = parameters
        self.activated: bool = activated
        self.dependency: str | None = dependency

    def copy_from_response(self, response_data: dict[str, Any]):
        """Returns a new SettingsStage with updated parameter values.
        Used because of the stateless nature of the server.

        Args:
            response_data (dict[str, Any]): The response directly fed in from the frontend.

        Raises:
            KeyError: If there is no 'settings' key in the response_data

        Returns:
            SettingsStage: A new SettingsStage.
        """

        # Copy all parameters and set new default values
        parameters = deepcopy(self.parameters)
        for parameter in self.parameters:
            try:
                # Might raise another KeyError
                parameter.default = response_data[parameter.id]
            except KeyError:  # If its from another
                raise KeyError(
                    f'"{parameter.id}" not in response settings data!')

        return SettingsStage(self.unique_name, self.title, parameters,
                             self.activated, self.dependency)

    def serialize(
        self
    ) -> dict[str, Any]:  # Returns a dictionary to be sent to the frontend
        return {
            'title': self.title,
            'id': self.unique_name,
            'activated': self.activated,
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
        activated: bool,
        dependency: str | None,
    ) -> None:
        self.unique_name: str = unique_name
        self.title: str = title
        self.parameters: list[Parameter] = parameters
        self.plot: Any | None = plot
        self.activated: bool = activated
        self.dependency: str | None = dependency

    def copy_from_response(self, response_data: dict[str, Any]):
        """Returns a new PlotsStage with updated parameter values.
        Used because of the stateless nature of the server.

        Args:
            response_data (dict[str, Any]): The response directly fed in from the frontend.

        Raises:
            KeyError: If there is no 'plots' key in the response_data

        Returns:
            PlotsStage: A new PlotsStage.
        """

        # Copy all parameters and set new default values
        parameters = deepcopy(self.parameters)
        for parameter in self.parameters:
            try:
                # Might raise another KeyError
                parameter.default = response_data[parameter.id]
            except KeyError:  # If its from another
                raise KeyError(f'"{parameter.id}" not in response plots data!')
        return PlotsStage(self.unique_name, self.title, parameters, self.plot,
                          self.activated, self.dependency)

    def serialize(self) -> dict[str, Any]:
        return {
            'title': self.title,
            'id': self.unique_name,
            'plot': self.plot,
            'activated': self.activated,
            'dependency': self.dependency,
            'parameters':
            [parameter.serialize() for parameter in self.parameters],
        }

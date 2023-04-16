# from blockops.utils.params import Parameter, MultipleChoices

from typing import Any
from copy import deepcopy

from web.stage.parameters import Parameter
# TODO: Integrate the stage parameters and replace the blockops params


class DocsStage:

    def __init__(
        self,
        unique_name: str,
        title: str,
        text: str,
        activated: bool,
        dependency: str | None,
    ) -> None:
        self.unique_name: str = unique_name
        self.title: str = title
        self.text: str = text
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
        button_name: str,
        activated: bool,
        dependency: str | None,
    ) -> None:
        self.unique_name: str = unique_name
        self.title: str = title
        self.parameters: list[Parameter] = parameters
        self.button: str = button_name
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
        if 'settings' not in response_data.keys():
            raise KeyError(
                '"settings" not in response data. Should only be called with a frontend response!'
            )
        settings_data = response_data['settings']
        if self.unique_name not in settings_data.keys():
            raise KeyError(
                f'"{self.unique_name}" not in response settings data. Should only be called with a frontend response!'
            )
        data = settings_data[self.unique_name]

        # Copy all parameters and set new default values
        parameters = deepcopy(self.parameters)
        for parameter in parameters:
            # Might raise another KeyError
            parameter.default = data[parameter.id]

        return SettingsStage(self.unique_name, self.title, parameters,
                             self.button, self.activated, self.dependency)

    def serialize(
        self
    ) -> dict[str, Any]:  # Returns a dictionary to be sent to the frontend
        return {
            'title': self.title,
            'id': self.unique_name,
            'button': self.button,
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
        if 'plots' not in response_data.keys():
            raise KeyError(
                '"plots" not in response data. Should only be called with a frontend response!'
            )
        settings_data = response_data['plots']
        if self.unique_name not in settings_data.keys():
            raise KeyError(
                f'"{self.unique_name}" not in response plots data. Should only be called with a frontend response!'
            )
        data = settings_data[self.unique_name]

        # Copy all parameters and set new default values
        parameters = deepcopy(self.parameters)
        for parameter in parameters:
            # Might raise another KeyError
            parameter.default = data[parameter.id]

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

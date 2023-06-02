from copy import deepcopy
from typing import Any

from dynamic_site.stage.parameters import Parameter


class DocsStage:

    def __init__(
        self,
        title: str,
        text: str,
    ) -> None:
        self.title: str = title
        self.text: str = text

    def copy(self):
        """Returns a new DocsStage but as a copy.

        Returns:
            DocsStage. A new docs stage.
        """
        return DocsStage(
            self.title,
            self.text,
        )

    def serialize(self) -> dict[str, Any]:
        return {
            'title': self.title,
            'text': self.text,
        }


class SettingsStage:

    def __init__(
        self,
        unique_name: str,
        title: str,
        parameters: list[Parameter],
        folded: bool,
    ) -> None:
        self.unique_name: str = unique_name
        self.title: str = title
        self.parameters: list[Parameter] = parameters
        self.folded: bool = folded

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
                parameter.optional = response_data[parameter.id]
            except KeyError:  # If its from another
                raise KeyError(
                    f'"{parameter.id}" not in response settings data!')

        return SettingsStage(self.unique_name, self.title, parameters,
                             self.folded)

    def serialize(
        self
    ) -> dict[str, Any]:  # Returns a dictionary to be sent to the frontend
        return {
            'id': self.unique_name,
            'title': self.title,
            'parameters':
            [parameter.serialize() for parameter in self.parameters],
            'folded': self.folded
        }


class PlotsStage:

    def __init__(
        self,
        title: str,
        plot: Any | None,
    ) -> None:
        self.title: str = title
        self.plot: Any | None = plot

    def copy(self):
        """Returns a new PlotsStage but as a copy.

        Returns:
            PlotsStage. A new plots stage.
        """
        return PlotsStage(
            self.title,
            self.plot,
        )

    def serialize(self) -> dict[str, Any]:
        return {
            'title': self.title,
            'plot': self.plot,
        }

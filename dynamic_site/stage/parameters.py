from typing import Any
from enum import Enum

from dynamic_site.stage.utils import slugify


class WebType(Enum):
    Integer = 'Integer'
    PositiveInteger = 'PositiveInteger'
    StrictlyPositiveInteger = 'StrictlyPositiveInteger'
    PositiveFloat = 'PositiveFloat'
    Float = 'Float'
    Enumeration = 'Enumeration'
    FloatList = 'FloatList'
    Boolean = 'Boolean'


class Parameter:
    ids: list[str] = []  # Keep track of all ids to check for uniqueness.

    def __init__(
        self,
        unique_id: str,
        name: str,
        placeholder: str,
        doc: str,
        type: WebType,
        optional: bool,
        choices: list[str] | None,
        value: int | float | list[float] | str | None,
    ) -> None:
        """Create a new parameter.

        Args:
            unique_id (str): A unique and slugified id.
            name (str): The name of this parameter that will be displayed. Might be LaTeX Math (r'`\lam`').
            placeholder (str): The placeholder inside the parameter field.
            doc (str): The doc-string on hover.
            type (WebType): The type of this parameter.
            optional (bool): If the parameter is optional.
            choices (list[str] | None): Only if the WebType == Enumeration otherwise None.
            value (int | float | list[float] | str | None): If there exists a default value, then this value value should be set.
        """
        self.id: str = unique_id
        self.name: str = name
        self.placeholder: str = placeholder
        self.doc: str = doc
        self.type: WebType = type
        self.optional: bool = optional
        self.choices: list[
            str] | None = choices  # None if this is not an enumeration type
        self.value: int | float | list[
            float] | str | None = value  # None if no default value exists

        Parameter.check_id_uniqueness(self.id)

    def serialize(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'placeholder': self.placeholder,
            'doc': self.doc,
            'type': self.type.value,
            'optional': self.optional,
            'choices': self.choices,
            'value': self.value,
        }

    @classmethod
    def check_id_uniqueness(cls, i: str):
        """Checks for parameter id uniqueness.

        Args:
            i (str): The (hopefully) unique id.

        Raises:
            RuntimeError: If the id is not unique.
        """
        # TODO: This has to be updated!
        pass
        # if i in cls.ids:
        # raise RuntimeError(f'id "{i}" not unique. Must be unique!')
        # else:
        # cls.ids.append(i)


class Integer(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 optional: bool,
                 value: int | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc, WebType.Integer,
                         optional, None, value)


class PositiveInteger(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 optional: bool,
                 value: int | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc,
                         WebType.PositiveInteger, optional, None, value)


class StrictlyPositiveInteger(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 optional: bool,
                 value: int | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc,
                         WebType.StrictlyPositiveInteger, optional, None,
                         value)


class PositiveFloat(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 optional: bool,
                 value: float | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc,
                         WebType.PositiveFloat, optional, None, value)


class Float(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 optional: bool,
                 value: float | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc, WebType.Float,
                         optional, None, value)


class Enumeration(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 optional: bool,
                 choices: list[str],
                 value: str | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc,
                         WebType.Enumeration, optional, choices, value)


class FloatList(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 optional: bool,
                 value: list[float] | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc, WebType.FloatList,
                         optional, None, value)


class Boolean(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 optional: bool,
                 value: bool | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc, WebType.Boolean,
                         optional, None, value)

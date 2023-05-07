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
        choices: list[str] | None,
        default: int | float | list[float] | str | None,
    ) -> None:
        """Create a new parameter.

        Args:
            unique_id (str): A unique and slugified id.
            name (str): The name of this parameter that will be displayed. Might be LaTeX Math (r'`\lam`').
            placeholder (str): The placeholder inside the parameter field.
            doc (str): The doc-string on hover.
            type (WebType): The type of this parameter.
            choices (list[str] | None): Only if the WebType == Enumeration otherwise None.
            default (int | float | list[float] | str | None): If optional, then this default value should be set.
        """
        self.id: str = unique_id
        self.name: str = name
        self.placeholder: str = placeholder
        self.doc: str = doc
        self.type: WebType = type
        self.choices: list[
            str] | None = choices  # None if this is not an enumeration type
        self.default: int | float | list[
            float] | str | None = default  # None if not optional

        Parameter.check_id_uniqueness(self.id)

    def serialize(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'placeholder': self.placeholder,
            'doc': self.doc,
            'type': self.type.value,
            'choices': self.choices,
            'default': self.default,
        }

    @classmethod
    def check_id_uniqueness(cls, i: str):
        """Checks for parameter id uniqueness and also for a slugified id.

        Args:
            i (str): The (hopefully) slugified id.

        Raises:
            RuntimeError: If the id is not slugified.
            RuntimeError: If the id is not unique.
        """
        if slugify(i) != i:
            raise RuntimeError(
                f'id "{i}" is not slugified. Should be "{slugify(i)}".')
        if i in cls.ids:
            raise RuntimeError(f'id "{i}" not unique. Must be unique!')
        else:
            cls.ids.append(i)


class Integer(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 default: int | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc, WebType.Integer,
                         None, default)


class PositiveInteger(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 default: int | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc,
                         WebType.PositiveInteger, None, default)


class StrictlyPositiveInteger(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 default: int | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc,
                         WebType.StrictlyPositiveInteger, None, default)


class PositiveFloat(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 default: float | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc,
                         WebType.PositiveFloat, None, default)


class Float(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 default: float | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc, WebType.Float,
                         None, default)


class Enumeration(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 choices: list[str],
                 default: str | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc,
                         WebType.Enumeration, choices, default)


class FloatList(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 default: list[float] | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc, WebType.FloatList,
                         None, default)


class Boolean(Parameter):

    def __init__(self,
                 unique_id: str,
                 name: str,
                 placeholder: str,
                 doc: str,
                 default: bool | None = None) -> None:
        super().__init__(unique_id, name, placeholder, doc, WebType.Boolean,
                         None, default)

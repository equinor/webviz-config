from enum import Enum


class StrEnum(str, Enum):
    def __repr__(self) -> str:
        return self._value_  # pylint: disable=no-member

    def __str__(self) -> str:
        return self._value_  # pylint: disable=no-member

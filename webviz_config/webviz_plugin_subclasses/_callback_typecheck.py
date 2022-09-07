# pylint: disable=line-too-long
from typing import Any, Callable, get_origin, TypeVar
import inspect
from enum import Enum

T = TypeVar("T")


class ConversionError(Exception):
    pass


def convert(arg: Any, convert_to: T) -> T:
    # pylint: disable=too-many-return-statements
    additional_error_message: str = ""
    try:
        if inspect.isclass(convert_to) and issubclass(convert_to, Enum):
            return convert_to(arg)  # type: ignore[return-value]
        if convert_to is int:
            return int(arg)  # type: ignore[return-value]
        if convert_to is float:
            return float(arg)  # type: ignore[return-value]
        if convert_to is str:
            return str(arg)  # type: ignore[return-value]
        if convert_to is list and isinstance(arg, list):
            return arg  # type: ignore[return-value]
        if get_origin(convert_to) is list and isinstance(arg, list):
            if "__args__" in dir(convert_to):
                return [convert(a, convert_to.__args__[0]) for a in arg]  # type: ignore[attr-defined,return-value]
        if convert_to is dict and isinstance(arg, dict):
            return arg  # type: ignore[return-value]
        if get_origin(convert_to) is dict and isinstance(arg, dict):
            if "__args__" in dir(convert_to) and len(convert_to.__args__) == 2:  # type: ignore[attr-defined]
                return {  # type: ignore[return-value]
                    convert(key, convert_to.__args__[0]): convert(  # type: ignore[attr-defined]
                        value, convert_to.__args__[1]  # type: ignore[attr-defined]
                    )
                    for key, value in arg.items()
                }

    # pylint: disable=broad-except
    except Exception as exception:
        additional_error_message = f"\n\n{exception}"

    raise ConversionError(
        f"Argument of type '{type(arg)}' cannot be converted to type '{convert_to}'.{additional_error_message}"
    )


def callback_typecheck(func: Callable) -> Callable:
    signature = inspect.signature(func)
    argument_annotations: list = []

    for param in signature.parameters.values():
        argument_annotations.append(param.annotation)

    def wrapper(*_args) -> signature.return_annotation:  # type: ignore[no-untyped-def,name-defined]
        adjusted_args: list = []

        for index, arg in enumerate(_args):
            adjusted_args.append(convert(arg, argument_annotations[index]))

        return func(*adjusted_args)

    return wrapper

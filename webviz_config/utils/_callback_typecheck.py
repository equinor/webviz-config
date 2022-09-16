# pylint: disable=line-too-long
from typing import Any, Callable, get_origin, _TypedDictMeta, TypeVar, Union  # type: ignore[attr-defined]
import inspect

T = TypeVar("T")


class ConversionError(Exception):
    pass


def convert(arg: Any, convert_to: T) -> T:
    # pylint: disable=too-many-return-statements, too-many-branches, too-many-nested-blocks
    additional_error_message: str = ""
    try:
        if convert_to is None and arg is None:
            return None
        if inspect.isclass(convert_to) and not isinstance(convert_to, _TypedDictMeta):
            return convert_to(arg)
        if (
            isinstance(convert_to, _TypedDictMeta)
            and "__annotations__" in dir(convert_to)
            and isinstance(arg, dict)
        ):
            new_dict = convert_to()
            for key, value in arg.items():
                if key in list(convert_to.__annotations__.keys()):
                    new_dict[key] = convert(value, convert_to.__annotations__[key])
                else:
                    raise Exception(
                        f"""
                        Key '{key}' not allowed in '{convert_to}'.\n
                        Allowed keys are: {', '.join(list(convert_to.__annotations__.keys()))}
                        """
                    )

            if not convert_to.__total__ or len(new_dict.keys()) == len(
                convert_to.__annotations__.keys()
            ):
                return new_dict

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
        if get_origin(convert_to) is Union:
            if "__args__" in dir(convert_to):
                for convert_type in convert_to.__args__:  # type: ignore[attr-defined]
                    try:
                        if isinstance(arg, convert_type):
                            return arg
                    except TypeError:
                        pass
                for convert_type in convert_to.__args__:  # type: ignore[attr-defined]
                    try:
                        return convert(arg, convert_type)
                    except ConversionError:
                        pass

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

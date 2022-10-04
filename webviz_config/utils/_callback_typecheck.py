# pylint: disable=line-too-long
from typing import Any, Callable, get_args, get_origin, _TypedDictMeta, TypeVar, Union  # type: ignore[attr-defined]
import inspect

T = TypeVar("T")


class ConversionError(Exception):
    pass


def _isinstance(arg: Any, annotation: Any) -> bool:
    # pylint: disable=too-many-return-statements, too-many-branches
    if annotation is type(None) or annotation is None:
        return arg is None

    if annotation is Any:
        return True

    if get_origin(annotation) is None:
        try:
            return isinstance(arg, annotation)
        except TypeError:
            return False

    if get_origin(annotation) == Union:
        for annotation_arg in get_args(annotation):
            if _isinstance(arg, annotation_arg):
                return True

    if get_origin(annotation) is list and isinstance(arg, list):
        result = True
        type_args = get_args(annotation)
        if len(type_args) == 1:
            for annotation_arg in arg:
                result &= _isinstance(annotation_arg, type_args[0])
        return result

    if get_origin(annotation) is dict and isinstance(arg, dict):
        result = True
        type_args = get_args(annotation)
        if len(type_args) == 2:
            for key, value in arg.items():
                result &= _isinstance(key, type_args[0])
                result &= _isinstance(value, type_args[1])
        return result

    return False


def convert(arg: Any, convert_to: T) -> T:
    # pylint: disable=too-many-return-statements, too-many-branches
    additional_error_message: str = ""
    try:
        if _isinstance(arg, convert_to):
            return arg
        if (
            inspect.isclass(convert_to)
            and not isinstance(convert_to, _TypedDictMeta)
            and arg is not None
        ):
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
            return [convert(a, get_args(convert_to)[0]) for a in arg]  # type: ignore[return-value]
        if convert_to is dict and isinstance(arg, dict):
            return arg  # type: ignore[return-value]
        if get_origin(convert_to) is dict and isinstance(arg, dict):
            if len(get_args(convert_to)) == 2:
                return {  # type: ignore[return-value]
                    convert(key, get_args(convert_to)[0]): convert(
                        value, get_args(convert_to)[1]
                    )
                    for key, value in arg.items()
                }
        if get_origin(convert_to) is Union and "__args__" in dir(convert_to):
            for convert_type in get_args(convert_to):
                try:
                    return convert(arg, convert_type)
                except ConversionError:
                    pass

    # pylint: disable=broad-except
    except Exception as exception:
        additional_error_message = f"\n\nMore details:\n{exception}"

    raise ConversionError(
        f"Argument of type '{type(arg)}' cannot be converted to type '{convert_to}'.{additional_error_message}"
    )


def callback_typecheck(func: Callable) -> Callable:
    signature = inspect.signature(func)
    parameters = list(signature.parameters.values())

    def wrapper(*_args) -> signature.return_annotation:  # type: ignore[no-untyped-def,name-defined]
        adjusted_args: list = []

        for index, arg in enumerate(_args):
            try:
                adjusted_args.append(convert(arg, parameters[index].annotation))
            except ConversionError as exception:
                raise ConversionError(
                    f"Error while converting input to argument '{parameters[index].name}' of function '{func.__name__}' in file '{func.__globals__['__file__']}': {exception}"
                ) from exception

        return func(*adjusted_args)

    return wrapper

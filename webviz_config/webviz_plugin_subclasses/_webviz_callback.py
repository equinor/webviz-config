from typing import Any, Callable, cast, List, Union, NewType, TypeVar
from dash import Input, callback, State
from dataclasses import dataclass
import inspect


class WebvizCallbackError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class WebvizCallbackWrongTypeError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class EmptySlot:
    pass


T = TypeVar("T")
SlotType = Union[T, EmptySlot]


@dataclass(frozen=True)
class PluginSlotConnection:
    plugin_id: str
    view_id: str
    slot_name: str
    input: Union[State, Input]


def webviz_callback(*_args) -> Callable:

    """
    try:
        exec_context = inspect.currentframe().f_locals["caller"].f_locals["self"]
        slots = exec_context["slots"]
    except:
        raise WebvizCallbackException(
            "Could not extract execution context. Make sure you only call this function inside a class inheriting from ViewABC."
        )
    """

    def decorator(func: Callable) -> None:
        try:
            closure_vars = inspect.getclosurevars(func)
            slots = closure_vars[0]["self"].slots
        except:
            raise WebvizCallbackError(
                "Could not extract execution context. Make sure you only call this function inside a class inheriting from ViewABC."
            )
        adjusted_args: list = []
        enabled_args: List[bool] = []
        slot_indices: List[int] = []
        dep_index = 0

        for arg in _args:
            if isinstance(arg, SlotInput):
                if arg.slot_name in slots:
                    adjusted_args.append(slots[arg.slot_name])
                    enabled_args.append(True)
                else:
                    enabled_args.append(False)
                slot_indices.append(dep_index)
                dep_index += 1
            else:
                adjusted_args.append(arg)
                if isinstance(arg, Input) or isinstance(arg, State):
                    enabled_args.append(True)
                    dep_index += 1

        fullargspec = list(inspect.getfullargspec(func)[-1].values())[1:]

        # Check if arg types are correct
        for index, argspec in enumerate(fullargspec):
            if index in slot_indices and not argspec.__args__[-1] is EmptySlot:
                raise WebvizCallbackWrongTypeError(
                    "Arguments connected to a slot value must be of type 'SlotType'"
                )

        @callback(tuple(adjusted_args))
        def wrapper(*_args) -> Any:
            new_args = []
            index = 0
            for index, enabled in enumerate(enabled_args):
                if enabled:
                    new_args.append(_args[index])
                else:
                    new_args.append(EmptySlot)
            return func(*new_args)

    return decorator


class SlotInput:
    def __init__(self, slot_name: str):
        self._slot_name = slot_name

    @property
    def slot_name(self) -> str:
        return self._slot_name

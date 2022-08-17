from typing import Any, Callable, List
from dash import Input, callback, State

global_plugin_slots = {}  # {"myslot": Input("webviz-content-manager", "activeViewId")}


class SlotInput:
    def __init__(self, slot_name: str):
        self._slot_name = slot_name

    @property
    def slot_name(self) -> str:
        return self._slot_name


def webviz_callback(*_args, **_kwargs) -> Callable:
    adjusted_args: list = []
    enabled_args: List[bool] = []
    for arg in _args:
        if isinstance(arg, SlotInput):
            if arg.slot_name in global_plugin_slots:
                adjusted_args.append(global_plugin_slots[arg.slot_name])
                enabled_args.append(True)
            else:
                enabled_args.append(False)
        else:
            adjusted_args.append(arg)
            if isinstance(arg, Input) or isinstance(arg, State):
                enabled_args.append(True)

    def decorator(func: Callable) -> None:
        @callback(tuple(adjusted_args))
        def wrapper(*_args) -> Any:
            new_args = []
            index = 0
            for index, enabled in enumerate(enabled_args):
                if enabled:
                    new_args.append(_args[index])
                else:
                    new_args.append(None)
            return func(*new_args)

    return decorator

from typing import Callable, List, Optional, Type, Union
import abc


class LayoutBaseABC(abc.ABC):
    def __init__(self) -> None:
        self._custom_id = ""
        self._uuid = ""
        self._plugin_register_id_func: Optional[
            Callable[[Union[str, List[str]]], None]
        ] = None

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        self._plugin_register_id_func = func

    def _set_custom_id(self, custom_id: str) -> None:
        self._custom_id = custom_id

    def _set_uuid(self, uuid: str) -> None:
        self._uuid = uuid

        if self._plugin_register_id_func:
            self._plugin_register_id_func(uuid)

    def custom_uuid(self) -> str:
        return self._custom_id

    def uuid(self) -> str:
        return self._uuid

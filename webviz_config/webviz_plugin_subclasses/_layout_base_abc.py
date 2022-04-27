from typing import Callable, List, Optional, Union
import abc

from ._layout_uuid import LayoutUuid


class LayoutBaseABC(abc.ABC):
    def __init__(self) -> None:
        self._uuid = LayoutUuid()
        self._plugin_register_id_func: Optional[
            Callable[[Union[str, List[str]]], None]
        ] = None
        self._plugin_get_store_uuid_func: Optional[Callable[[str], str]] = None

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        self._plugin_register_id_func = func

    def _set_uuid(self, parent_uuid: LayoutUuid) -> None:
        self._uuid.adopt(parent_uuid)

        if self._plugin_register_id_func:
            self._plugin_register_id_func(str(self._uuid))

    def get_uuid(self) -> LayoutUuid:
        return self._uuid

    def _set_plugin_get_store_uuid_func(self, func: Callable[[str], str]) -> None:
        self._plugin_get_store_uuid_func = func

    def get_store_uuid(self, store_id: str) -> str:
        if self._plugin_get_store_uuid_func:
            return self._plugin_get_store_uuid_func(store_id)

        raise NotImplementedError("This element has not been added to any plugin yet.")

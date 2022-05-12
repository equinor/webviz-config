from typing import Callable, List, Optional, Union
import abc

from ._layout_unique_id import LayoutUniqueId


class LayoutBaseABC(abc.ABC):
    def __init__(self) -> None:
        self._unique_id = LayoutUniqueId()
        self._plugin_register_id_func: Optional[
            Callable[[Union[str, List[str]]], None]
        ] = None
        self._plugin_get_store_unique_id_func: Optional[Callable[[str], str]] = None

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        self._plugin_register_id_func = func

    def _set_unique_id(self, parent_unique_id: LayoutUniqueId) -> None:
        self._unique_id.adopt(parent_unique_id)

        if self._plugin_register_id_func:
            self._plugin_register_id_func(str(self._unique_id))

    def get_unique_id(self) -> LayoutUniqueId:
        return self._unique_id

    def _set_plugin_get_store_unique_id_func(self, func: Callable[[str], str]) -> None:
        self._plugin_get_store_unique_id_func = func

    def get_store_unique_id(self, store_id: str) -> str:
        if self._plugin_get_store_unique_id_func:
            return self._plugin_get_store_unique_id_func(store_id)

        raise NotImplementedError("This element has not been added to a plugin yet.")

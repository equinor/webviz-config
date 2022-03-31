from typing import Callable, List, Optional, Union
import abc

from ._layout_uuid import LayoutUuid


class LayoutBaseABC(abc.ABC):
    def __init__(self) -> None:
        self._uuid = LayoutUuid()
        self._plugin_register_id_func: Optional[
            Callable[[Union[str, List[str]]], None]
        ] = None

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

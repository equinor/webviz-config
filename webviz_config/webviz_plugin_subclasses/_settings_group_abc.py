from typing import Callable, List, Optional, Type, Union
import abc

from dash.development.base_component import Component  # type: ignore
from dash import Dash  # type: ignore
import webviz_core_components as wcc  # type: ignore


class SettingsGroupABC(abc.ABC):
    def __init__(self, title: str) -> None:
        super().__init__()

        self.title = title
        self._uuid = ""
        self._plugin_register_id_func: Optional[
            Callable[[Union[str, List[str]]], None]
        ] = None
        self._layout_created: bool = False

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        self._plugin_register_id_func = func

    def _set_uuid(self, uuid: str) -> None:
        self._uuid = uuid

        if self._plugin_register_id_func:
            self._plugin_register_id_func(uuid)

    def register_component_uuid(self, component_name: str) -> str:
        id = self.component_uuid(component_name)
        if self._plugin_register_id_func and not self._layout_created:
            self._plugin_register_id_func(id)

        return id

    def component_uuid(self, component_name: str) -> str:
        return f"{component_name}-{self._uuid}"

    def uuid(self) -> str:
        return self._uuid

    @property
    @abc.abstractmethod
    def layout(self) -> Type[Component]:
        raise NotImplementedError

    def _wrapped_layout(
        self, view_id: Optional[str] = "", plugin_id: Optional[str] = ""
    ) -> Type[Component]:
        layout = wcc.WebvizSettingsGroup(
            id=self.uuid(),
            title=self.title,
            viewId=view_id,
            pluginId=plugin_id,
            children=[self.layout()],
        )
        self._layout_created = True
        return layout

    def _set_callbacks(self, app: Dash) -> None:
        pass

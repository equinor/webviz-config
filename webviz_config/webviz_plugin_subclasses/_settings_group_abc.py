from typing import Callable, List, Optional, Type, Union
import abc

from dash.development.base_component import Component  # type: ignore
from dash import Dash  # type: ignore
import webviz_core_components as wcc  # type: ignore

from ._layout_base_abc import LayoutBaseABC


class SettingsGroupABC(LayoutBaseABC):
    def __init__(self, title: str) -> None:
        super().__init__()

        self.title = title
        self._layout_created: bool = False
        self._visible_in_views: List[str] = []
        self._not_visible_in_views: List[str] = []

    def _set_visible_in_views(self, visible_in_views: List[str]) -> None:
        self._visible_in_views = visible_in_views

    def _set_not_visible_in_views(self, not_visible_in_views: List[str]) -> None:
        self._not_visible_in_views = not_visible_in_views

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        self._plugin_register_id_func = func

    def register_component_uuid(self, component_name: str) -> str:
        uuid = self.component_uuid(component_name)
        if self._plugin_register_id_func and not self._layout_created:
            self._plugin_register_id_func(uuid)

        return uuid

    def component_uuid(self, component_name: str) -> str:
        return f"{component_name}-{self._uuid}"

    @abc.abstractmethod
    def layout(self) -> Type[Component]:
        raise NotImplementedError

    def _wrapped_layout(
        self,
        view_id: Optional[str] = "",
        plugin_id: Optional[str] = "",
        always_open: bool = False,
    ) -> Type[Component]:
        layout = wcc.WebvizSettingsGroup(
            id=self.uuid(),
            title=self.title,
            viewId=view_id,
            pluginId=plugin_id,
            visibleInViews=self._visible_in_views
            if len(self._visible_in_views) > 0
            else None,
            notVisibleInViews=self._not_visible_in_views
            if len(self._not_visible_in_views) > 0
            else None,
            alwaysOpen=always_open,
            children=[self.layout()],
        )
        self._layout_created = True
        return layout

    def _set_callbacks(self, app: Dash) -> None:
        pass

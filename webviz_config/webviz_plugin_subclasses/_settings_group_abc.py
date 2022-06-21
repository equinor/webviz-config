from typing import Callable, List, Optional, Type, Union
import abc

from dash.development.base_component import Component
import webviz_core_components as wcc

from ._layout_base_abc import LayoutBaseABC
from ._layout_unique_id import LayoutUniqueId


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

    def register_component_unique_id(self, component_name: str) -> str:
        uuid = self.component_unique_id(component_name).to_string()
        if self._plugin_register_id_func and not self._layout_created:
            self._plugin_register_id_func(uuid)

        return uuid

    def component_unique_id(self, component_name: str) -> LayoutUniqueId:
        component_uuid = LayoutUniqueId(other=self.get_unique_id())
        component_uuid.set_component_id(component_name)
        return component_uuid

    @abc.abstractmethod
    def layout(self) -> Union[List[Component], Type[Component]]:
        raise NotImplementedError

    def _wrapped_layout(
        self,
        view_id: Optional[str] = "",
        plugin_id: Optional[str] = "",
        always_open: bool = False,
    ) -> Type[Component]:
        layout = self.layout()
        wrapped_layout = wcc.WebvizSettingsGroup(
            id=str(self.get_unique_id()),
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
            children=layout if isinstance(layout, list) else [layout],
        )
        self._layout_created = True
        return wrapped_layout

    def set_callbacks(self) -> None:
        pass

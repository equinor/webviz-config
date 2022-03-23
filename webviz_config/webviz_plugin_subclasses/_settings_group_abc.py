from typing import Optional, Type
import abc

from uuid import uuid4

from dash.development.base_component import Component
from dash import Dash

import webviz_core_components as wcc


class SettingsGroupABC(abc.ABC):
    def __init__(self, title: str) -> None:
        super().__init__()

        self.title = title
        self._uuid = ""

    def _set_uuid(self, uuid: str) -> None:
        self._uuid = uuid

    def uuid(self, element: Optional[str] = None) -> str:
        if element:
            return f"{element}-{self._uuid}"
        return self._uuid

    @property
    @abc.abstractmethod
    def layout(self) -> Type[Component]:
        raise NotImplementedError

    def _wrapped_layout(
        self, view_id: Optional[str] = "", plugin_id: Optional[str] = ""
    ) -> Type[Component]:
        return wcc.WebvizSettingsGroup(
            id=self.uuid(),
            title=self.title,
            viewId=view_id,
            pluginId=plugin_id,
            children=[self.layout()],
        )

    def _set_callbacks(self, app: Dash) -> None:
        return

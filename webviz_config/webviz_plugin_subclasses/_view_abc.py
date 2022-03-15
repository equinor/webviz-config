from typing import Optional, Type
import abc

from typing import List
from uuid import uuid4

from dash import html

import webviz_core_components as wcc

from ._view_element_abc import ViewElementABC
from ._settings_group_abc import SettingsGroupABC

from dash.development.base_component import Component


class ViewABC(abc.ABC):
    def __init__(self, name: str) -> None:
        super().__init__()

        self._uuid: str = str(uuid4())
        self.name = name

    def uuid(self, element: Optional[str] = None) -> str:
        if element:
            return f"{element}-{self._uuid}"
        return self._uuid

    def view_elements(self) -> List[ViewElementABC]:
        raise NotImplementedError

    def settings(self) -> List[SettingsGroupABC]:
        return []

    def layout(self) -> Type[Component]:
        return html.Div(
            [
                wcc.WebvizViewElement(
                    id=el.uuid("view-element"), children=[el.layout()]
                )
                for el in self.view_elements()
            ]
        )

    def as_dict(self) -> dict:
        return {
            "id": self._uuid,
            "name": self.name,
        }

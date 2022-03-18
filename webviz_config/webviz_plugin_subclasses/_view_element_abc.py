from typing import List, Optional, Type, Union
import abc
from uuid import uuid4

from ._settings_group_abc import SettingsGroupABC

from dash import Dash, Input, Output
from dash.development.base_component import Component


class ViewElementABC(abc.ABC):
    def __init__(
        self,
        screenshot_filename: str = "webviz-screenshot.png",
    ) -> None:
        super().__init__()

        self._uuid: str = ""
        self._screenshot_filename = screenshot_filename
        self._add_download_button = False

        self._settings: List[SettingsGroupABC] = []

    def _set_uuid(self, uuid: str) -> None:
        self._uuid = uuid

        for setting in self._settings:
            setting._set_uuid(f"{uuid}-{setting.uuid()}")

    def uuid(self, element: Optional[str] = None) -> str:
        if element is None:
            return self._uuid
        return f"{element}-{self._uuid}"

    def add_settings_group(
        self, settings_group: SettingsGroupABC, id: Optional[str] = None
    ) -> None:
        uuid = f"{self._uuid}-" if self._uuid != "" else ""
        if id:
            uuid += id
        else:
            uuid += f"settings{len(self._settings)}"

        settings_group._set_uuid(uuid)
        self._settings.append(settings_group)

    @property
    def view_element_data_output(self) -> Output:
        self._add_download_button = True
        return Output(self.uuid(), "download")

    @property
    def view_element_data_requested(self) -> Input:
        return Input(self.uuid(), "data_requested")

    def layout(self) -> Union[str, Type[Component]]:
        raise NotImplementedError

    def settings(self) -> Optional[Type[Component]]:
        return None

    def as_dict(self) -> dict:
        return {"id": self._uuid, "layout": self.layout(), "settings": self.settings()}

    def _set_all_callbacks(self, app: Dash) -> None:
        for setting in self._settings:
            setting._set_callbacks(app)

        self._set_callbacks(app)

    def _set_callbacks(self, app: Dash) -> None:
        return

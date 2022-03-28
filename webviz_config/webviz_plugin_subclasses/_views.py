from typing import List, Optional, Type, Union
import abc
from enum import Enum

from dash import html, Dash, Input, Output # type: ignore
from dash.development.base_component import Component # type: ignore
import webviz_core_components as wcc # type: ignore

from ._settings_group_abc import SettingsGroupABC


class ViewElementABC(abc.ABC):
    def __init__(
        self, flex_grow: int = 1, screenshot_filename: str = "webviz-screenshot.png"
    ) -> None:
        super().__init__()

        self._flex_grow = flex_grow
        self._uuid: str = ""
        self._screenshot_filename = screenshot_filename
        self._add_download_button = False

        self._settings: List[SettingsGroupABC] = []

    def _set_uuid(self, uuid: str) -> None:
        self._uuid = uuid

        for setting in self._settings:
            # pylint: disable=protected-access
            setting._set_uuid(f"{uuid}-{setting.uuid()}")

    def uuid(self, element: Optional[str] = None) -> str:
        if element is None:
            return self._uuid
        return f"{element}-{self._uuid}"

    def add_settings_group(
        self, settings_group: SettingsGroupABC, settings_group_id: Optional[str] = None
    ) -> None:
        uuid = f"{self._uuid}-" if self._uuid != "" else ""
        if settings_group_id:
            uuid += settings_group_id
        else:
            uuid += f"settings{len(self._settings)}"

        # pylint: disable=protected-access
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

    def settings(self) -> List[SettingsGroupABC]:
        return self._settings

    def _set_all_callbacks(self, app: Dash) -> None:
        for setting in self._settings:
            # pylint: disable=protected-access
            setting._set_callbacks(app)

        self._set_callbacks(app)

    def _set_callbacks(self, app: Dash) -> None:
        pass


class LayoutElementType(Enum):
    ROW = 1
    COLUMN = 2


class ViewLayoutElement:
    def __init__(
        self, layout_element_type: LayoutElementType, parent_view: "ViewABC", flex_grow: int = 1
    ):
        self._parent_view: ViewABC = parent_view
        self._children: List[Union[ViewLayoutElement, ViewElementABC]] = []
        self._flex_grow = flex_grow
        self.__type = layout_element_type

    def make_row(self, flex_grow: int = 1) -> "ViewLayoutElement":
        row = ViewLayoutElement(LayoutElementType.ROW, self._parent_view, flex_grow)
        self._children.append(row)
        return row

    def add_column(self, column: "ViewLayoutElement") -> None:
        self._children.append(column)

    def make_column(self, flex_grow: int = 1) -> "ViewLayoutElement":
        column = ViewLayoutElement(
            LayoutElementType.COLUMN, self._parent_view, flex_grow
        )
        self._children.append(column)
        return column

    def add_view_element(
        self, view_element: ViewElementABC, view_element_id: Optional[str] = None
    ) -> None:
        # pylint: disable=protected-access
        self._parent_view._add_view_element(view_element, view_element_id)
        self._children.append(view_element)

    def add_view_elements(self, view_elements: List[ViewElementABC]) -> None:
        for view_element in view_elements:
            self.add_view_element(view_element)

    def _set_all_callbacks(self, app: Dash) -> None:
        for child in self._children:
            # pylint: disable=protected-access
            child._set_all_callbacks(app)

    def _set_uuid(self, uuid: str) -> None:
        # pylint: disable=protected-access
        for child in self._children:
            if isinstance(child, ViewElementABC):
                child._set_uuid(f"{uuid}-{child.uuid()}")
            else:
                child._set_uuid(uuid)

    @property
    def layout(self) -> Type[Component]:
        # pylint: disable=protected-access
        if self.__type == LayoutElementType.ROW:
            return wcc.WebvizPluginLayoutRow(
                flexGrow=self._flex_grow,
                children=[
                    wcc.WebvizViewElement(
                        id=el.uuid(),
                        # pylint: disable=protected-access
                        showDownload=el._add_download_button,
                        flexGrow=el._flex_grow,
                        children=[
                            el.layout(),
                            *[setting._wrapped_layout() for setting in el.settings()],
                        ],
                    )
                    if isinstance(el, ViewElementABC)
                    else el.layout()
                    for el in self._children
                ],
            )
        return wcc.WebvizPluginLayoutColumn(
            flexGrow=self._flex_grow,
            children=[
                wcc.WebvizViewElement(
                    id=el.uuid(),
                    showDownload=el._add_download_button,
                    flexGrow=el._flex_grow,
                    children=[
                        el.layout(),
                        *[setting._wrapped_layout() for setting in el.settings()],
                    ],
                )
                if isinstance(el, ViewElementABC)
                else el.layout()
                for el in self._children
            ],
        )


class ViewABC(abc.ABC):
    def __init__(self, name: str) -> None:
        super().__init__()

        self._uuid = ""
        self.name = name

        self._layout_elements: List[Union[ViewElementABC, ViewLayoutElement]] = []
        self._view_elements: List[ViewElementABC] = []
        self._settings_groups: List[SettingsGroupABC] = []

    def _set_uuid(self, uuid: str) -> None:
        # pylint: disable=protected-access
        self._uuid = uuid
        for element in self._layout_elements:
            if isinstance(element, ViewElementABC):
                element._set_uuid(f"{uuid}-{element.uuid()}")
            else:
                element._set_uuid(uuid)

        for setting in self._settings_groups:
            setting._set_uuid(f"{uuid}-{setting.uuid()}")

    def uuid(self, element: Optional[str] = None) -> str:
        if element:
            return f"{element}-{self._uuid}"
        return self._uuid

    def view_element_uuid(self, view_id: str, element: Optional[str]) -> str:
        if element:
            return f"{element}-{self._uuid}-{view_id}"
        return f"{self._uuid}-{view_id}"

    def view_element(self, view_element_id: str) -> "ViewElementABC":
        view_element = next(
            (el for el in self.view_elements() if el.uuid().split("-")[-1] == view_element_id), None
        )
        if view_element:
            return view_element

        raise LookupError(
            f"""Invalid view element id: '{view_element_id}. 
            Available view element ids: {[el.uuid for el in self.view_elements()]}
            """
        )

    def settings_group(self, settings_group_id: str) -> SettingsGroupABC:
        settings_group = next(
            (el for el in self.settings_groups() if el.uuid().split("-")[-1] == settings_group_id),
            None,
        )
        if settings_group:
            return settings_group

        raise LookupError(
            f"""Invalid settings group id: '{settings_group_id}. 
            Available settings group ids: {[el.uuid for el in self.settings_groups()]}
            """
        )

    def settings_group_uuid(self, settings_id: str, element: Optional[str]) -> str:
        if element:
            return f"{element}-{self._uuid}-{settings_id}"
        return f"{self._uuid}-{settings_id}"

    def add_view_element(
        self, view_element: ViewElementABC, view_element_id: Optional[str] = None
    ) -> None:
        # pylint: disable=protected-access
        uuid = f"{self._uuid}-" if self._uuid != "" else ""
        if view_element_id is not None:
            uuid += view_element_id
        else:
            uuid += f"element{len(self._view_elements)}"

        view_element._set_uuid(uuid)
        self._layout_elements.append(view_element)
        self._view_elements.append(view_element)

    def _add_view_element(
        self, view_element: ViewElementABC, view_element_id: Optional[str] = None
    ) -> None:
        # pylint: disable=protected-access
        uuid = f"{self._uuid}-" if self._uuid != "" else ""
        if view_element_id is not None:
            uuid += view_element_id
        else:
            uuid += f"element{len(self._view_elements)}"

        view_element._set_uuid(uuid)
        self._view_elements.append(view_element)

    def add_row(self, flex_grow: int = 1) -> ViewLayoutElement:
        row = ViewLayoutElement(LayoutElementType.ROW, self, flex_grow)
        self._layout_elements.append(row)
        return row

    def add_column(self, flex_grow: int = 1) -> ViewLayoutElement:
        column = ViewLayoutElement(LayoutElementType.COLUMN, self, flex_grow)
        self._layout_elements.append(column)
        return column

    def add_view_elements(self, view_elements: List[ViewElementABC]) -> None:
        for view_element in view_elements:
            self.add_view_element(view_element)

    def add_settings_group(
        self, settings_group: SettingsGroupABC, settings_group_id: Optional[str] = None
    ) -> None:
        # pylint: disable=protected-access
        uuid = f"{self._uuid}-" if self._uuid != "" else ""
        if settings_group_id is not None:
            uuid += settings_group_id
        else:
            uuid += f"element{len(self._settings_groups)}"

        settings_group._set_uuid(uuid)
        self._settings_groups.append(settings_group)

    def add_settings_groups(self, settings_groups: List[SettingsGroupABC]) -> None:
        for settings_group in settings_groups:
            self.add_settings_group(settings_group)

    def _set_all_callbacks(self, app: Dash) -> None:
        # pylint: disable=protected-access
        for element in self._view_elements:
            element._set_all_callbacks(app)

        for setting in self._settings_groups:
            setting._set_callbacks(app)

        self._set_callbacks(app)

    def view_elements(self) -> List[ViewElementABC]:
        return self._view_elements

    def settings_groups(self) -> List[SettingsGroupABC]:
        return self._settings_groups

    def layout(self) -> Type[Component]:
        # pylint: disable=protected-access
        return html.Div(
            [
                wcc.WebvizViewElement(
                    id=el.uuid(),
                    showDownload=el._add_download_button,
                    flexGrow=el._flex_grow,
                    children=[
                        el.layout(),
                        *[setting._wrapped_layout() for setting in el.settings()],
                    ],
                )
                if isinstance(el, ViewElementABC)
                else el.layout
                for el in self._layout_elements
            ]
        )

    def _set_callbacks(self, app: Dash) -> None:
        pass

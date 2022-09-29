from typing import Callable, cast, Dict, List, Optional, Type, Union
from enum import Enum
from uuid import uuid4

from dash import Input, Output
from dash.development.base_component import Component
import webviz_core_components as wcc

from ._settings_group_abc import SettingsGroupABC
from ._layout_base_abc import LayoutBaseABC
from ._layout_unique_id import LayoutUniqueId


class NoParentPlugin(Exception):
    pass


class UnknownId(Exception):
    pass


class ViewElementABC(LayoutBaseABC):
    def __init__(
        self, flex_grow: int = 1, screenshot_filename: str = "webviz-screenshot.png"
    ) -> None:
        super().__init__()

        self._flex_grow = flex_grow
        self._screenshot_filename = screenshot_filename
        self._add_download_button = False

        self._settings: List[SettingsGroupABC] = []
        self._layout_created: bool = False

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        super()._set_plugin_register_id_func(func)

        for setting in self._settings:
            # pylint: disable=protected-access
            setting._set_plugin_register_id_func(func)

    def _set_plugin_get_store_unique_id_func(self, func: Callable[[str], str]) -> None:
        super()._set_plugin_get_store_unique_id_func(func)
        # pylint: disable=protected-access
        for setting in self._settings:
            setting._set_plugin_get_store_unique_id_func(func)

    def _set_unique_id(self, parent_unique_id: LayoutUniqueId) -> None:
        super()._set_unique_id(parent_unique_id)

        for setting in self._settings:
            # pylint: disable=protected-access
            setting._set_unique_id(self.get_unique_id())

    def set_flex_grow(self, flex_grow: int) -> None:
        self._flex_grow = flex_grow

    def register_component_unique_id(self, component_name: str) -> str:
        uuid = self.component_unique_id(component_name).to_string()
        if self._plugin_register_id_func and not self._layout_created:
            self._plugin_register_id_func(uuid)

        return uuid

    def component_unique_id(self, component_name: str) -> LayoutUniqueId:
        component_unique_id = LayoutUniqueId(other=self.get_unique_id())
        component_unique_id.set_component_id(component_name)
        return component_unique_id

    def add_settings_group(
        self, settings_group: SettingsGroupABC, settings_group_id: str
    ) -> None:
        # pylint: disable=protected-access
        settings_group.get_unique_id().set_settings_group_id(settings_group_id)
        settings_group._set_unique_id(self._unique_id)
        self._settings.append(settings_group)

    def setting_group_unique_id(
        self, settings_id: str, element: Optional[str] = None
    ) -> str:
        setting = next(
            (
                el
                for el in self.settings_groups()
                if el.get_unique_id().get_settings_group_id() == settings_id
            ),
            None,
        )
        if not setting:
            available_ids = [
                cast(str, el.get_unique_id().get_settings_group_id())
                for el in self.settings_groups()
                if el.get_unique_id().get_settings_group_id() is not None
            ]
            raise UnknownId(
                f"Could not find settings group with id '{settings_id}'.\n"
                f"Available ids are: {' ,'.join(available_ids)}"
            )

        uuid = LayoutUniqueId(other=setting.get_unique_id())
        if element:
            uuid.set_component_id(element)
        return uuid.to_string()

    def settings_group(self, settings_group_id: str) -> SettingsGroupABC:
        settings_group = next(
            (
                el
                for el in self.settings_groups()
                if el.get_unique_id().get_settings_group_id() == settings_group_id
            ),
            None,
        )
        if settings_group:
            return settings_group

        raise LookupError(
            f"""Invalid settings group id: '{settings_group_id}.
            Available settings group ids: {[
                el.get_unique_id().get_settings_group_id()
                for el in self.settings_groups()
            ]}
            """
        )

    def view_element_data_output(self) -> Output:
        self._add_download_button = True
        return Output(str(self.get_unique_id().to_string()), "download")

    def view_element_data_requested(self) -> Input:
        return Input(str(self.get_unique_id().to_string()), "data_requested")

    def _wrapped_layout(self) -> Union[str, Type[Component]]:
        layout = self.inner_layout()
        self._layout_created = True
        return layout

    def outer_layout(self) -> Type[Component]:
        # pylint: disable=protected-access
        return wcc.WebvizViewElement(
            id=str(self.get_unique_id()),
            showDownload=self._add_download_button,
            flexGrow=self._flex_grow,
            children=[
                self._wrapped_layout(),
                *[
                    setting._wrapped_layout(always_open=True)
                    for setting in self.settings_groups()
                ],
            ],
        )

    def inner_layout(self) -> Union[str, Type[Component]]:
        raise NotImplementedError

    def settings_groups(self) -> List[SettingsGroupABC]:
        return self._settings

    def _set_all_callbacks(self) -> None:
        for setting in self._settings:
            setting.set_callbacks()

        self.set_callbacks()

    def set_callbacks(self) -> None:
        pass


class LayoutElementType(Enum):
    ROW = 1
    COLUMN = 2


class ViewLayoutElement(LayoutBaseABC):
    def __init__(
        self,
        layout_element_type: LayoutElementType,
        parent_view: "ViewABC",
        flex_grow: int = 1,
    ):
        super().__init__()

        self._parent_view: ViewABC = parent_view
        self._children: List[Union[ViewLayoutElement, ViewElementABC]] = []
        self._flex_grow = flex_grow
        self.__type = layout_element_type

    def make_row(
        self, row_id: Optional[str] = None, flex_grow: int = 1
    ) -> "ViewLayoutElement":
        # pylint: disable=protected-access
        if row_id is None:
            row_id = str(uuid4())
        row = ViewLayoutElement(LayoutElementType.ROW, self._parent_view, flex_grow)
        row._set_unique_id(self._unique_id)
        row.get_unique_id().set_view_element_id(row_id)
        self._children.append(row)
        self._parent_view._add_layout_element(row, row_id)
        return row

    def make_column(
        self, column_id: Optional[str] = None, flex_grow: int = 1
    ) -> "ViewLayoutElement":
        # pylint: disable=protected-access
        if column_id is None:
            column_id = str(uuid4())
        column = ViewLayoutElement(
            LayoutElementType.COLUMN, self._parent_view, flex_grow
        )
        column._set_unique_id(self._unique_id)
        column.get_unique_id().set_view_element_id(column_id)
        self._children.append(column)
        self._parent_view._add_layout_element(column, column_id)
        return column

    def add_row(self, row: "ViewLayoutElement", row_id: Optional[str] = None) -> None:
        # pylint: disable=protected-access
        row_id = row_id if row_id is not None else str(uuid4())
        row._set_unique_id(self.get_unique_id())
        row.get_unique_id().set_view_element_id(row_id)
        self._parent_view._add_layout_element(row, row_id)
        self._children.append(row)

    def add_column(
        self, column: "ViewLayoutElement", column_id: Optional[str] = None
    ) -> None:
        # pylint: disable=protected-access
        column_id = column_id if column_id is not None else str(uuid4())
        column._set_unique_id(self.get_unique_id())
        column.get_unique_id().set_view_element_id(column_id)
        self._parent_view._add_layout_element(column, column_id)
        self._children.append(column)

    def add_view_element(
        self, view_element: ViewElementABC, view_element_id: str, flex_grow: int = 1
    ) -> None:
        # pylint: disable=protected-access
        view_element.set_flex_grow(flex_grow)
        self._parent_view._add_view_element(view_element, view_element_id)
        self._children.append(view_element)

    def add_view_elements(self, view_elements: Dict[str, ViewElementABC]) -> None:
        for view_element_id, view_element in view_elements.items():
            self.add_view_element(view_element, view_element_id)

    def _set_all_callbacks(self) -> None:
        for child in self._children:
            # pylint: disable=protected-access
            child._set_all_callbacks()

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        super()._set_plugin_register_id_func(func)
        for element in self._children:
            # pylint: disable=protected-access
            element._set_plugin_register_id_func(func)

    def _set_plugin_get_store_unique_id_func(self, func: Callable[[str], str]) -> None:
        super()._set_plugin_get_store_unique_id_func(func)
        # pylint: disable=protected-access
        for element in self._children:
            element._set_plugin_get_store_unique_id_func(func)

    def _set_unique_id(self, parent_unique_id: LayoutUniqueId) -> None:
        # pylint: disable=protected-access
        super()._set_unique_id(parent_unique_id)

        for child in self._children:
            child._set_unique_id(parent_unique_id)

    @property
    def layout(self) -> Type[Component]:
        # pylint: disable=protected-access
        if self.__type == LayoutElementType.ROW:
            return wcc.WebvizPluginLayoutRow(
                id=str(self.get_unique_id()),
                flexGrow=self._flex_grow,
                children=[
                    wcc.WebvizViewElement(
                        id=str(el.get_unique_id()),
                        # pylint: disable=protected-access
                        showDownload=el._add_download_button,
                        flexGrow=el._flex_grow,
                        children=[
                            el._wrapped_layout(),
                            *[
                                setting._wrapped_layout(always_open=True)
                                for setting in el.settings_groups()
                            ],
                        ],
                    )
                    if isinstance(el, ViewElementABC)
                    else el.layout
                    for el in self._children
                ],
            )
        return wcc.WebvizPluginLayoutColumn(
            id=str(self.get_unique_id()),
            flexGrow=self._flex_grow,
            children=[
                wcc.WebvizViewElement(
                    id=str(el.get_unique_id()),
                    showDownload=el._add_download_button,
                    flexGrow=el._flex_grow,
                    children=[
                        el._wrapped_layout(),
                        *[
                            setting._wrapped_layout(always_open=True)
                            for setting in el.settings_groups()
                        ],
                    ],
                )
                if isinstance(el, ViewElementABC)
                else el.layout
                for el in self._children
            ],
        )


# pylint: disable=too-many-public-methods
class ViewABC(LayoutBaseABC):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

        self._add_download_button = False
        self._child_elements: List[Union[ViewElementABC, ViewLayoutElement]] = []
        self._view_elements: List[ViewElementABC] = []
        self._layout_elements: List[ViewLayoutElement] = []
        self._settings_groups: List[SettingsGroupABC] = []
        self._plugin_register_id_func: Optional[
            Callable[[Union[str, List[str]]], None]
        ] = None
        self._get_plugin_shared_settings: Optional[
            Callable[[], List[SettingsGroupABC]]
        ] = None

    def shared_settings_group(self, settings_group_id: str) -> SettingsGroupABC:
        if not self._get_plugin_shared_settings:
            raise NoParentPlugin(
                f"The view {self.name} has not been added to a plugin yet."
            )
        settings_group = next(
            (
                el
                for el in self._get_plugin_shared_settings()
                if el.get_unique_id().get_settings_group_id() == settings_group_id
            ),
            None,
        )
        if settings_group:
            return settings_group

        raise LookupError(
            f"""Invalid shared settings group id: '{settings_group_id}.
            Available shared settings group ids: {[
                el.get_unique_id().get_settings_group_id()
                for el in self._get_plugin_shared_settings()
            ]}
            """
        )

    def shared_settings_group_unique_id(
        self, settings_id: str, element: Optional[str] = None
    ) -> str:
        if not self._get_plugin_shared_settings:
            raise NoParentPlugin(
                f"The view {self.name} has not been added to a plugin yet."
            )
        setting = next(
            (
                el
                for el in self._get_plugin_shared_settings()
                if el.get_unique_id().get_settings_group_id() == settings_id
            ),
            None,
        )
        if not setting:
            available_ids = [
                cast(str, el.get_unique_id().get_settings_group_id())
                for el in self._get_plugin_shared_settings()
                if el.get_unique_id().get_settings_group_id() is not None
            ]
            raise UnknownId(
                f"Could not find settings group with id '{settings_id}'.\n"
                f"Available ids are: {' ,'.join(available_ids)}"
            )

        uuid = LayoutUniqueId(other=setting.get_unique_id())
        if element:
            uuid.set_component_id(element)
        return uuid.to_string()

    def _set_get_plugin_shared_settings_func(
        self, func: Callable[[], List[SettingsGroupABC]]
    ) -> None:
        self._get_plugin_shared_settings = func

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        # pylint: disable=protected-access
        self._plugin_register_id_func = func
        for element in self._child_elements:
            element._set_plugin_register_id_func(func)

        for setting in self._settings_groups:
            setting._set_plugin_register_id_func(func)

    def _set_plugin_get_store_unique_id_func(self, func: Callable[[str], str]) -> None:
        super()._set_plugin_get_store_unique_id_func(func)
        # pylint: disable=protected-access
        for element in self._child_elements:
            element._set_plugin_get_store_unique_id_func(func)

        for setting in self._settings_groups:
            setting._set_plugin_get_store_unique_id_func(func)

    def _set_unique_id(self, parent_unique_id: LayoutUniqueId) -> None:
        # pylint: disable=protected-access
        super()._set_unique_id(parent_unique_id)

        for element in self._child_elements:
            element._set_unique_id(self.get_unique_id())

        for setting in self._settings_groups:
            setting._set_unique_id(self.get_unique_id())

    def unique_id(self, element: Optional[str] = None) -> str:
        if element:
            return f"{element}-{self._unique_id}"
        return str(self._unique_id)

    def view_element_unique_id(
        self, view_element_id: str, element: Optional[str] = None
    ) -> str:
        view_element = next(
            (
                el
                for el in self.view_elements()
                if el.get_unique_id().get_view_element_id() == view_element_id
            ),
            None,
        )
        if not view_element:
            available_ids = [
                cast(str, el.get_unique_id().get_view_element_id())
                for el in self.view_elements()
                if el.get_unique_id().get_view_element_id() is not None
            ]
            raise UnknownId(
                f"Could not find view element with id '{view_element_id}'.\n"
                f"Available ids are: {' ,'.join(available_ids)}"
            )

        uuid = LayoutUniqueId(other=view_element.get_unique_id())
        if element:
            uuid.set_component_id(element)
        return uuid.to_string()

    def view_element(self, view_element_id: str) -> "ViewElementABC":
        view_element = next(
            (
                el
                for el in self.view_elements()
                if el.get_unique_id().get_view_element_id() == view_element_id
            ),
            None,
        )
        if view_element:
            return view_element

        raise LookupError(
            f"""Invalid view element id: '{view_element_id}.
            Available view element ids: {[
                el.get_unique_id().get_view_element_id()
                for el in self.view_elements()
            ]}
            """
        )

    def layout_element(self, layout_element_id: str) -> "ViewLayoutElement":
        layout_element = next(
            (
                el
                for el in self.layout_elements()
                if el.get_unique_id().get_view_element_id() == layout_element_id
            ),
            None,
        )
        if layout_element:
            return layout_element

        raise LookupError(
            f"""Invalid layout element id: '{layout_element_id}.
            Available layout element ids: {[
                el.get_unique_id().get_view_element_id()
                for el in self.layout_elements()
            ]}
            """
        )

    def settings_group(self, settings_group_id: str) -> SettingsGroupABC:
        settings_group = next(
            (
                el
                for el in self.settings_groups()
                if el.get_unique_id().get_settings_group_id() == settings_group_id
            ),
            None,
        )
        if settings_group:
            return settings_group

        raise LookupError(
            f"""Invalid settings group id: '{settings_group_id}.
            Available settings group ids: {[
                el.get_unique_id().get_settings_group_id()
                for el in self.settings_groups()
            ]}
            """
        )

    def settings_group_unique_id(
        self, settings_id: str, element: Optional[str] = None
    ) -> str:
        setting = next(
            (
                el
                for el in self.settings_groups()
                if el.get_unique_id().get_settings_group_id() == settings_id
            ),
            None,
        )
        if not setting:
            available_ids = [
                cast(str, el.get_unique_id().get_settings_group_id())
                for el in self.settings_groups()
                if el.get_unique_id().get_settings_group_id() is not None
            ]
            raise UnknownId(
                f"Could not find settings group with id '{settings_id}'.\n"
                f"Available ids are: {' ,'.join(available_ids)}"
            )

        uuid = LayoutUniqueId(other=setting.get_unique_id())
        if element:
            uuid.set_component_id(element)
        return uuid.to_string()

    def add_view_element(
        self, view_element: ViewElementABC, view_element_id: str
    ) -> None:
        # pylint: disable=protected-access
        view_element._set_unique_id(self._unique_id)
        view_element.get_unique_id().set_view_element_id(view_element_id)
        self._child_elements.append(view_element)
        self._view_elements.append(view_element)

    def _add_view_element(
        self, view_element: ViewElementABC, view_element_id: str
    ) -> None:
        # pylint: disable=protected-access
        view_element._set_unique_id(self._unique_id)
        view_element.get_unique_id().set_view_element_id(view_element_id)
        self._view_elements.append(view_element)

    def _add_layout_element(
        self, layout_element: ViewLayoutElement, layout_element_id: str
    ) -> None:
        # pylint: disable=protected-access
        layout_element._set_unique_id(self._unique_id)
        layout_element.get_unique_id().set_view_element_id(layout_element_id)
        self._layout_elements.append(layout_element)

    def add_row(
        self, layout_element_id: Optional[str] = None, flex_grow: int = 1
    ) -> ViewLayoutElement:
        row = ViewLayoutElement(LayoutElementType.ROW, self, flex_grow)
        layout_element_id = (
            layout_element_id if layout_element_id is not None else str(uuid4())
        )
        row.get_unique_id().set_view_element_id(layout_element_id)
        self._layout_elements.append(row)
        self._child_elements.append(row)
        return row

    def add_column(
        self, layout_element_id: Optional[str] = None, flex_grow: int = 1
    ) -> ViewLayoutElement:
        column = ViewLayoutElement(LayoutElementType.COLUMN, self, flex_grow)
        layout_element_id = (
            layout_element_id if layout_element_id is not None else str(uuid4())
        )
        column.get_unique_id().set_view_element_id(layout_element_id)
        self._layout_elements.append(column)
        self._child_elements.append(column)
        return column

    def add_view_elements(self, view_elements: Dict[str, ViewElementABC]) -> None:
        for view_element_id, view_element in view_elements.items():
            self.add_view_element(view_element, view_element_id)

    def remove_view_element(self, view_element_id: str) -> bool:
        old_length = len(self._view_elements)
        self._view_elements = [
            view_element
            for view_element in self._view_elements
            if view_element.get_unique_id().get_view_element_id() == view_element_id
        ]
        return old_length != len(self._view_elements)

    def add_settings_group(
        self, settings_group: SettingsGroupABC, settings_group_id: str
    ) -> None:
        # pylint: disable=protected-access
        settings_group._set_unique_id(self._unique_id)
        settings_group.get_unique_id().set_settings_group_id(settings_group_id)
        self._settings_groups.append(settings_group)

    def add_settings_groups(self, settings_groups: Dict[str, SettingsGroupABC]) -> None:
        for settings_group_id, settings_group in settings_groups.items():
            self.add_settings_group(settings_group, settings_group_id)

    def _set_all_callbacks(self) -> None:
        # pylint: disable=protected-access
        for element in self._view_elements:
            element._set_all_callbacks()

        for setting in self._settings_groups:
            setting.set_callbacks()

        self.set_callbacks()

    def view_elements(self) -> List[ViewElementABC]:
        return self._view_elements

    def layout_elements(self) -> List[ViewLayoutElement]:
        return self._layout_elements

    def settings_groups(self) -> List[SettingsGroupABC]:
        return self._settings_groups

    def view_data_output(self) -> Output:
        self._add_download_button = True
        return Output(str(self.get_unique_id().to_string()), "download")

    def view_data_requested(self) -> Input:
        return Input(str(self.get_unique_id().to_string()), "data_requested")

    def inner_layout(self) -> List[Type[Component]]:
        return [
            el.outer_layout() if isinstance(el, ViewElementABC) else el.layout
            for el in self._child_elements
        ]

    def outer_layout(self) -> Type[Component]:
        return wcc.WebvizView(
            id=str(self.get_unique_id()),
            children=self.inner_layout(),
        )

    def set_callbacks(self) -> None:
        pass

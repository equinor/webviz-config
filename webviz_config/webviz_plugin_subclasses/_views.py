from typing import Callable, cast, Dict, List, Optional, Type, Union
from enum import Enum

from dash import html, Dash, Input, Output  # type: ignore
from dash.development.base_component import Component  # type: ignore
import webviz_core_components as wcc  # type: ignore

from ._settings_group_abc import SettingsGroupABC
from ._layout_base_abc import LayoutBaseABC
from ._layout_uuid import LayoutUuid


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
        self._plugin_register_id_func: Optional[
            Callable[[Union[str, List[str]]], None]
        ] = None

        self._settings: List[SettingsGroupABC] = []
        self._layout_created: bool = False

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        super()._set_plugin_register_id_func(func)

        for setting in self._settings:
            # pylint: disable=protected-access
            setting._set_plugin_register_id_func(func)

    def _set_uuid(self, parent_uuid: LayoutUuid) -> None:
        super()._set_uuid(parent_uuid)

        for setting in self._settings:
            # pylint: disable=protected-access
            setting._set_uuid(self.get_uuid())

    def register_component_uuid(self, component_name: str) -> str:
        uuid = self.component_uuid(component_name).to_string()
        if self._plugin_register_id_func and not self._layout_created:
            self._plugin_register_id_func(uuid)

        return uuid

    def component_uuid(self, component_name: str) -> LayoutUuid:
        component_uuid = LayoutUuid(other=self.get_uuid())
        component_uuid.set_component_id(component_name)
        return component_uuid

    def add_settings_group(
        self, settings_group: SettingsGroupABC, settings_group_id: str
    ) -> None:
        # pylint: disable=protected-access
        settings_group.get_uuid().set_settings_group_id(settings_group_id)
        settings_group._set_uuid(self._uuid)
        self._settings.append(settings_group)

    def setting_group_uuid(
        self, settings_id: str, element: Optional[str] = None
    ) -> str:
        setting = next(
            (
                el
                for el in self.settings_groups()
                if el.get_uuid().get_settings_group_id() == settings_id
            ),
            None,
        )
        if not setting:
            available_ids = [
                cast(str, el.get_uuid().get_settings_group_id())
                for el in self.settings_groups()
                if el.get_uuid().get_settings_group_id() != None
            ]
            raise UnknownId(
                f"Could not find settings group with id '{settings_id}'.\n"
                f"Available ids are: {' ,'.join(available_ids)}"
            )

        uuid = LayoutUuid(other=setting.get_uuid())
        if element:
            uuid.set_component_id(element)
        return uuid.to_string()

    @property
    def view_element_data_output(self) -> Output:
        self._add_download_button = True
        return Output(str(self.get_uuid()), "download")

    @property
    def view_element_data_requested(self) -> Input:
        return Input(str(self.get_uuid()), "data_requested")

    def _wrapped_layout(self) -> Union[str, Type[Component]]:
        layout = self.layout()
        self._layout_created = True
        return layout

    def layout(self) -> Union[str, Type[Component]]:
        raise NotImplementedError

    def settings_groups(self) -> List[SettingsGroupABC]:
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
        self,
        layout_element_type: LayoutElementType,
        parent_view: "ViewABC",
        flex_grow: int = 1,
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
        self, view_element: ViewElementABC, view_element_id: str
    ) -> None:
        # pylint: disable=protected-access
        self._parent_view._add_view_element(view_element, view_element_id)
        self._children.append(view_element)

    def add_view_elements(self, view_elements: Dict[str, ViewElementABC]) -> None:
        for view_element_id, view_element in view_elements.items():
            self.add_view_element(view_element, view_element_id)

    def _set_all_callbacks(self, app: Dash) -> None:
        for child in self._children:
            # pylint: disable=protected-access
            child._set_all_callbacks(app)

    def _set_plugin_register_id_func(
        self, func: Callable[[Union[str, List[str]]], None]
    ) -> None:
        for element in self._children:
            # pylint: disable=protected-access
            element._set_plugin_register_id_func(func)

    def _set_uuid(self, uuid: LayoutUuid) -> None:
        # pylint: disable=protected-access
        for child in self._children:
            if isinstance(child, ViewElementABC):
                child._set_uuid(uuid)
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
                        id=str(el.get_uuid()),
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
            flexGrow=self._flex_grow,
            children=[
                wcc.WebvizViewElement(
                    id=str(el.get_uuid()),
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


class ViewABC(LayoutBaseABC):
    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name

        self._layout_elements: List[Union[ViewElementABC, ViewLayoutElement]] = []
        self._view_elements: List[ViewElementABC] = []
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
                if el.get_uuid().get_settings_group_id() == settings_group_id
            ),
            None,
        )
        if settings_group:
            return settings_group

        raise LookupError(
            f"""Invalid shared settings group id: '{settings_group_id}. 
            Available shared settings group ids: {
                [el.get_uuid().get_settings_group_id() for el in self._get_plugin_shared_settings()]
            }
            """
        )

    def shared_settings_group_uuid(
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
                if el.get_uuid().get_settings_group_id() == settings_id
            ),
            None,
        )
        if not setting:
            available_ids = [
                cast(str, el.get_uuid().get_settings_group_id())
                for el in self._get_plugin_shared_settings()
                if el.get_uuid().get_settings_group_id() != None
            ]
            raise UnknownId(
                f"Could not find settings group with id '{settings_id}'.\n"
                f"Available ids are: {' ,'.join(available_ids)}"
            )

        uuid = LayoutUuid(other=setting.get_uuid())
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
        for element in self._layout_elements:
            element._set_plugin_register_id_func(func)

        for setting in self._settings_groups:
            setting._set_plugin_register_id_func(func)

    def _set_uuid(self, parent_uuid: LayoutUuid) -> None:
        # pylint: disable=protected-access
        super()._set_uuid(parent_uuid)

        for element in self._layout_elements:
            element._set_uuid(self.get_uuid())

        for setting in self._settings_groups:
            setting._set_uuid(self.get_uuid())

    def uuid(self, element: Optional[str] = None) -> str:
        if element:
            return f"{element}-{self._uuid}"
        return str(self._uuid)

    def view_element_uuid(
        self, view_element_id: str, element: Optional[str] = None
    ) -> str:
        view_element = next(
            (
                el
                for el in self.view_elements()
                if el.get_uuid().get_view_element_id() == view_element_id
            ),
            None,
        )
        if not view_element:
            available_ids = [
                cast(str, el.get_uuid().get_view_element_id())
                for el in self.view_elements()
                if el.get_uuid().get_view_element_id() != None
            ]
            raise UnknownId(
                f"Could not find view element with id '{view_element_id}'.\n"
                f"Available ids are: {' ,'.join(available_ids)}"
            )

        uuid = LayoutUuid(other=view_element.get_uuid())
        if element:
            uuid.set_component_id(element)
        return uuid.to_string()

    def view_element(self, view_element_id: str) -> "ViewElementABC":
        view_element = next(
            (
                el
                for el in self.view_elements()
                if el.get_uuid().get_view_element_id() == view_element_id
            ),
            None,
        )
        if view_element:
            return view_element

        raise LookupError(
            f"""Invalid view element id: '{view_element_id}. 
            Available view element ids: {[el.get_uuid().get_view_element_id() for el in self.view_elements()]}
            """
        )

    def settings_group(self, settings_group_id: str) -> SettingsGroupABC:
        settings_group = next(
            (
                el
                for el in self.settings_groups()
                if el.get_uuid().get_settings_group_id() == settings_group_id
            ),
            None,
        )
        if settings_group:
            return settings_group

        raise LookupError(
            f"""Invalid settings group id: '{settings_group_id}. 
            Available settings group ids: {[el.get_uuid().get_settings_group_id() for el in self.settings_groups()]}
            """
        )

    def settings_group_uuid(
        self, settings_id: str, element: Optional[str] = None
    ) -> str:
        setting = next(
            (
                el
                for el in self.settings_groups()
                if el.get_uuid().get_settings_group_id() == settings_id
            ),
            None,
        )
        if not setting:
            available_ids = [
                cast(str, el.get_uuid().get_settings_group_id())
                for el in self.settings_groups()
                if el.get_uuid().get_settings_group_id() != None
            ]
            raise UnknownId(
                f"Could not find settings group with id '{settings_id}'.\n"
                f"Available ids are: {' ,'.join(available_ids)}"
            )

        uuid = LayoutUuid(other=setting.get_uuid())
        if element:
            uuid.set_component_id(element)
        return uuid.to_string()

    def add_view_element(
        self, view_element: ViewElementABC, view_element_id: str
    ) -> None:
        # pylint: disable=protected-access
        view_element._set_uuid(self._uuid)
        view_element.get_uuid().set_view_element_id(view_element_id)
        self._layout_elements.append(view_element)
        self._view_elements.append(view_element)

    def _add_view_element(
        self, view_element: ViewElementABC, view_element_id: str
    ) -> None:
        # pylint: disable=protected-access
        view_element._set_uuid(self._uuid)
        view_element.get_uuid().set_view_element_id(view_element_id)
        self._view_elements.append(view_element)

    def add_row(self, flex_grow: int = 1) -> ViewLayoutElement:
        row = ViewLayoutElement(LayoutElementType.ROW, self, flex_grow)
        self._layout_elements.append(row)
        return row

    def add_column(self, flex_grow: int = 1) -> ViewLayoutElement:
        column = ViewLayoutElement(LayoutElementType.COLUMN, self, flex_grow)
        self._layout_elements.append(column)
        return column

    def add_view_elements(self, view_elements: Dict[str, ViewElementABC]) -> None:
        for view_element_id, view_element in view_elements.items():
            self.add_view_element(view_element, view_element_id)

    def add_settings_group(
        self, settings_group: SettingsGroupABC, settings_group_id: str
    ) -> None:
        # pylint: disable=protected-access
        settings_group._set_uuid(self._uuid)
        settings_group.get_uuid().set_settings_group_id(settings_group_id)
        self._settings_groups.append(settings_group)

    def add_settings_groups(self, settings_groups: Dict[str, SettingsGroupABC]) -> None:
        for settings_group_id, settings_group in settings_groups.items():
            self.add_settings_group(settings_group, settings_group_id)

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
            className="WebvizPluginWrapper__DashContent",
            children=[
                wcc.WebvizViewElement(
                    id=str(el.get_uuid()),
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
                for el in self._layout_elements
            ],
        )

    def _set_callbacks(self, app: Dash) -> None:
        pass

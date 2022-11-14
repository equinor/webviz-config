from typing import Dict, List, Optional, Tuple, Type, Union
import io
import abc
import base64
import zipfile
import warnings
import sys
import urllib
import enum

import bleach
from dash.development.base_component import Component
from dash import callback, callback_context, dcc, html, Input, Output
import dash
import jinja2
import webviz_core_components as wcc

from .webviz_plugin_subclasses import SettingsGroupABC, ViewABC, LayoutUniqueId

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class ZipFileMember(TypedDict):
    filename: str  # Filename to be given within the archive
    content: str  # String representing file content


class EncodedFile(ZipFileMember):
    # Same keys as in ZipFileMember, with the following changes:
    # - filename is now name of the actual downloaded file.
    # - content is now a base64 encoded ASCII string.
    # - mime_type needs to be added as well.
    mime_type: str


def _create_feedback_text(
    plugin_name: str, dist_name: str, dist_version: str, dependencies: Dict[str, str]
) -> str:
    template_environment = jinja2.Environment(  # nosec
        loader=jinja2.PackageLoader("webviz_config", "templates"),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )
    template = template_environment.get_template("feedback.md.jinja2")
    return template.render(
        {
            "plugin_name": plugin_name,
            "dist_name": dist_name,
            "dist_version": dist_version,
            "dependencies": dependencies,
        }
    )


class DuplicatePluginChildId(Exception):
    pass


class WebvizPluginABC(abc.ABC):
    # pylint: disable=too-many-public-methods
    """All webviz plugins need to subclass this abstract base class,
    e.g.

    ```python
    class MyPlugin(WebvizPluginABC):

        def __init__(self):
            ...

        def layout(self):
            ...
    ```
    """

    # This is the default set of buttons to show in the rendered plugin
    # toolbar. If the list is empty, the subclass plugin layout will be
    # used directly, without any visual encapsulation layout from this
    # abstract base class. The plugins subclassing this abstract base class
    # can override this variable setting by defining a class constant with
    # the same name.
    #
    # Some buttons will only appear if in addition necessary data is available.
    # E.g. download of zip archive will only appear if the plugin also
    # has defined the corresponding callback, and contact person will only
    # appear if the user configuration file has this information.

    # List of plugin specific assets which should be copied
    # over to the ./assets folder in the generated webviz app.
    # This is typically custom JavaScript and/or CSS files.
    # All paths in the returned ASSETS list should be absolute.
    ASSETS: list = []

    # Counter for instances of the same plugin.
    # Used to create unique ids of DOM elements
    CLASS_INSTANCE_COUNTER: int = 0

    class StorageType(enum.Enum):
        MEMORY = "memory"
        LOCAL = "local"
        SESSION = "session"

    def __init__(
        self,
        screenshot_filename: str = "webviz-screenshot.png",
        stretch: bool = False,
    ) -> None:
        """If a plugin/subclass defines its own `__init__` function
        (which they usually do), they should remember to call
        ```python
        super().__init__()
        ```
        in its own `__init__` function in order to also run the parent `__init__`.
        """
        self.__class__.CLASS_INSTANCE_COUNTER += 1

        self._plugin_unique_id = LayoutUniqueId(
            plugin_uuid=f"{type(self).__name__}-{self.__class__.CLASS_INSTANCE_COUNTER}"
        )
        self._screenshot_filename = screenshot_filename
        self._add_download_button = False

        self._views: List[Tuple[str, ViewABC]] = []
        self._stores: List[Tuple[str, WebvizPluginABC.StorageType]] = []
        self._shared_settings_groups: List[SettingsGroupABC] = []
        self._registered_ids: List[str] = []

        self._active_view_id = ""
        self._stretch = stretch
        self._all_callbacks_set = False

        self._legacy_plugin_view_id = f"{self._plugin_unique_id.to_string()}-view"

        self._set_wrapper_callbacks()

    def uuid(self, element: Optional[str] = None) -> str:
        """Typically used to get a unique ID for some given element/component in
        a plugins layout. If the element string is unique within the plugin, this
        function returns a string which is guaranteed to be unique also across the
        application (even when multiple instances of the same plugin is added).

        Within the same plugin instance, the returned uuid is the same for the same
        element string. I.e. storing the returned value in the plugin is not necessary.

        Main benefit of using this function instead of creating a UUID directly,
        is that the abstract base class can in the future provide IDs that
        are consistent across application restarts (i.e. when the webviz configuration
        file changes in a non-portable setting).
        """

        if element is None:
            return f"{self._plugin_unique_id.get_plugin_uuid()}"

        return f"{element}-{self._plugin_unique_id.get_plugin_uuid()}"

    def set_stretch(self, stretch: bool) -> None:
        self._stretch = stretch

    @property
    def layout(self) -> Union[str, Type[Component]]:
        """This is the only required function of a Webviz plugin.
        It returns a Dash layout which by webviz-config is added to
        the main Webviz application.
        """
        raise NotImplementedError

    def _check_and_register_id(self, id_or_list_of_ids: Union[str, List[str]]) -> None:
        for i in list(
            id_or_list_of_ids
            if isinstance(id_or_list_of_ids, list)
            else [id_or_list_of_ids]
        ):
            if i in self._registered_ids:
                raise DuplicatePluginChildId(
                    f"Duplicate ID in plugin '{type(self).__name__}' detected: '{i}'"
                )
            self._registered_ids.append(i)

    def add_view(self, view: ViewABC, view_id: str, view_group: str = "") -> None:
        # pylint: disable=protected-access
        view.get_unique_id().set_view_id(view_id)
        view._set_get_plugin_shared_settings_func(self.shared_settings_groups)
        view._set_plugin_register_id_func(self._check_and_register_id)
        view._set_plugin_get_store_unique_id_func(self.get_store_unique_id)
        view._set_unique_id(self._plugin_unique_id)
        self._views.append((view_group, view))

    def add_shared_settings_group(
        self,
        settings_group: SettingsGroupABC,
        settings_group_id: str,
        visible_in_views: Optional[List[str]] = None,
        not_visible_in_views: Optional[List[str]] = None,
    ) -> None:
        settings_group.get_unique_id().set_settings_group_id(settings_group_id)
        # pylint: disable=protected-access
        settings_group._set_visible_in_views(
            visible_in_views if visible_in_views else []
        )
        settings_group._set_not_visible_in_views(
            not_visible_in_views if not_visible_in_views else []
        )
        settings_group._set_plugin_register_id_func(self._check_and_register_id)
        settings_group._set_plugin_get_store_unique_id_func(self.get_store_unique_id)
        settings_group._set_unique_id(self._plugin_unique_id)
        self._shared_settings_groups.append(settings_group)

    def add_store(self, store_id: str, storage_type: StorageType) -> None:
        self._stores.append((store_id, storage_type))

    def get_store_unique_id(self, store_id: str) -> str:
        store = next((el[0] for el in self._stores if el[0] == store_id))
        if store:
            return self.uuid(f"store-{store}")

        raise LookupError(
            f"Invalid store id: '{store_id}. Available store ids: {[el[0] for el in self._stores]}"
        )

    def _set_callbacks(self) -> None:
        pass

    def _set_all_callbacks(self) -> None:
        if not self._all_callbacks_set:
            # pylint: disable=protected-access
            self._set_callbacks()
            for view in self._views:
                view[1]._set_all_callbacks()

            for settings_group in self._shared_settings_groups:
                settings_group.set_callbacks()

            self._all_callbacks_set = True

    @property
    def active_view_id(self) -> str:
        return self._active_view_id

    def set_active_view_id(self, view_id: str) -> None:
        view = self.view(view_id)
        if view:
            self._active_view_id = view.get_unique_id().to_string()

    def views(self, view_group: str = "") -> List[Tuple[str, ViewABC]]:
        if view_group != "":
            return list(filter(lambda x: x[0] == view_group, self._views))
        return self._views

    def view(self, view_id: str) -> ViewABC:
        view = next(
            (
                el[1]
                for el in self.views()
                if el[1].get_unique_id().get_view_id() == view_id
            ),
            None,
        )
        if view:
            return view

        raise LookupError(
            f"""
            Invalid view id: '{view_id}. Available view ids: {[
                el[1].get_unique_id().get_view_id() for el in self._views
            ]}
            """
        )

    def unverified_view_uuid(self, view_id: str) -> str:
        view_uuid = LayoutUniqueId(self._plugin_unique_id.get_plugin_uuid(), view_id)
        return view_uuid.to_string()

    def unverified_settings_group_uuid(self, group_id: str) -> str:
        group_uuid = LayoutUniqueId(self._plugin_unique_id.get_plugin_uuid(), group_id)
        return group_uuid.to_string()

    def shared_settings_groups(self) -> List[SettingsGroupABC]:
        return self._shared_settings_groups

    def shared_settings_group(self, settings_group_id: str) -> SettingsGroupABC:
        group = next(
            (
                el
                for el in self.shared_settings_groups()
                if el.get_unique_id().get_settings_group_id() == settings_group_id
            ),
            None,
        )
        if group:
            return group

        raise LookupError(
            f"""
            Invalid settings group id: '{settings_group_id}'.
            Available settings group ids: {[
                    el.get_unique_id().get_settings_group_id()
                    for el in self._shared_settings_groups
                ]}
            """
        )

    def get_all_settings(self) -> List[html.Div]:
        # pylint: disable=protected-access
        settings = []
        shared_settings = self.shared_settings_groups()
        if shared_settings is not None:
            settings = [
                setting._wrapped_layout("", self._plugin_unique_id.to_string())
                for setting in shared_settings
            ]

        for view in self._views:
            settings.extend(
                [
                    setting._wrapped_layout(
                        view[1].unique_id(), self._plugin_unique_id.to_string()
                    )
                    for setting in view[1].settings_groups()
                ]
            )

        return settings

    @property
    def plugin_data_output(self) -> Output:
        self._add_download_button = True
        return Output(self._legacy_plugin_view_id, "download")

    @property
    def plugin_data_requested(self) -> Input:
        return Input(self._legacy_plugin_view_id, "data_requested")

    @staticmethod
    def _reformat_tour_steps(steps: List[dict]) -> List[dict]:
        return [
            {
                "elementId": str(step["id"]),
                "viewId": ""
                if isinstance(step["id"], str)
                else step["id"].get_view_unique_id()
                if step["id"].get_view_unique_id() is not None
                else "",
                "settingsGroupId": ""
                if isinstance(step["id"], str)
                else step["id"].get_settings_group_unique_id()
                if step["id"].is_settings_group()
                else None,
                "viewElementId": ""
                if isinstance(step["id"], str)
                else step["id"].get_view_element_unique_id()
                if step["id"].is_view_element() and step["id"].is_settings_group()
                else None,
                "content": step["content"],
            }
            for step in steps
        ]

    @staticmethod
    def plugin_compressed_data(
        filename: str, content: List[ZipFileMember]
    ) -> EncodedFile:
        with io.BytesIO() as bytes_io:
            with zipfile.ZipFile(bytes_io, "w") as zipped_data:
                for data in content:
                    zipped_data.writestr(data["filename"], data["content"])
            return {
                "filename": filename,
                "content": base64.b64encode(bytes_io.getvalue()).decode("ascii"),
                "mime_type": "application/zip",
            }

    @staticmethod
    def plugin_data_compress(content: List[ZipFileMember]) -> EncodedFile:
        warnings.warn(
            "Use 'plugin_compressed_data' instead of 'plugin_data_compress'",
            DeprecationWarning,
        )
        return WebvizPluginABC.plugin_compressed_data("webviz-data.zip", content)

    def _make_extended_deprecation_warnings(
        self,
        plugin_deprecation_warnings: Optional[List[str]] = None,
        argument_deprecation_warnings: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        # pylint: disable=import-outside-toplevel
        from .plugins import PLUGIN_METADATA, PLUGIN_PROJECT_METADATA

        extended_deprecation_warnings: List[Dict[str, str]] = []

        plugin_name = self.__class__.__name__
        dist_name = PLUGIN_METADATA[plugin_name]["dist_name"]
        metadata = PLUGIN_PROJECT_METADATA[dist_name]

        if plugin_deprecation_warnings:
            url = (
                f"{metadata['documentation_url']}/#/plugin_deprecations?id={plugin_name.lower()}"
                if metadata["documentation_url"] is not None
                else ""
            )

            for plugin_deprecation_warning in plugin_deprecation_warnings:
                extended_deprecation_warnings.append(
                    {"message": plugin_deprecation_warning, "url": url}
                )
        if argument_deprecation_warnings:
            url = (
                f"{metadata['documentation_url']}/#/argument_deprecations?id={plugin_name.lower()}"
                if metadata["documentation_url"] is not None
                else ""
            )

            for argument_deprecation_warning in argument_deprecation_warnings:
                extended_deprecation_warnings.append(
                    {"message": argument_deprecation_warning, "url": url}
                )
        return extended_deprecation_warnings

    def _make_feedback_url(self) -> str:
        # pylint: disable=import-outside-toplevel
        from .plugins import PLUGIN_METADATA, PLUGIN_PROJECT_METADATA

        plugin_name = self.__class__.__name__
        dist_name = PLUGIN_METADATA[plugin_name]["dist_name"]
        metadata = PLUGIN_PROJECT_METADATA[dist_name]

        feedback_url = ""
        if metadata["tracker_url"] is not None:
            queries = {
                "title": "",
                "body": _create_feedback_text(
                    plugin_name,
                    dist_name,
                    metadata["dist_version"],
                    metadata["dependencies"],
                ),
            }

            feedback_url = (
                f"{metadata['tracker_url']}/new?{urllib.parse.urlencode(queries)}"
                if "github.com" in metadata["tracker_url"]
                else metadata["tracker_url"]
            )

        return feedback_url

    def plugin_layout(
        self,
        contact_person: Optional[dict] = None,
        plugin_deprecation_warnings: Optional[List[str]] = None,
        argument_deprecation_warnings: Optional[List[str]] = None,
    ) -> List[Component]:
        """This function returns plugin layout placed within a WebvizPluginWrapper
        component, which contains a settings drawer with useful buttons like fullscreen
        and screenshot of plugin content. Additional buttons as plugin author contact
        information, download of data, guided tour, issue feedback link, etc. will appear
        based on provided information.

        Button for download of data will only appear if corresponding
        callback functionality is implemented for the respective plugin.
        """

        self._set_all_callbacks()

        if self.active_view_id == "" and len(self.views()) > 0:
            self._active_view_id = self.views()[0][1].get_unique_id().to_string()

        if contact_person:
            # Sanitize the configuration user input
            for key in contact_person:
                contact_person[key] = bleach.clean(str(contact_person[key]))

        return [
            dcc.Store(
                id=self.uuid(f"store-{store[0]}"),
                storage_type=store[1].value,
            )
            for store in self._stores
        ] + [
            wcc.WebvizPluginWrapper(
                id=self._plugin_unique_id.to_string(),
                name=type(self).__name__,
                views=[
                    {
                        "id": view[1].unique_id(),
                        "group": view[0],
                        "name": view[1].name,
                        # pylint: disable=protected-access
                        "showDownload": view[1]._add_download_button,
                    }
                    for view in self.views()
                ]
                if self.views()
                else [
                    {
                        "id": self._legacy_plugin_view_id,
                        "group": "",
                        "name": "",
                        "showDownload": self._add_download_button,
                    }
                ],
                initiallyActiveViewId=self.active_view_id
                if self.views()
                else self._legacy_plugin_view_id,
                contactPerson=contact_person,
                deprecationWarnings=self._make_extended_deprecation_warnings(
                    plugin_deprecation_warnings, argument_deprecation_warnings
                ),
                screenshotFilename=self._screenshot_filename,
                feedbackUrl=self._make_feedback_url(),
                tourSteps=WebvizPluginABC._reformat_tour_steps(self.tour_steps)
                if hasattr(self, "tour_steps")
                else None,
                stretch=self._stretch if self.views() else True,
                children=[
                    wcc.WebvizPluginLoadingIndicator()
                    if self.views()
                    else wcc.WebvizView(
                        id=self._legacy_plugin_view_id,
                        children=[
                            html.Div(
                                children=[self.layout],
                                style={"width": "100%", "margin-left": "16px"},
                            )
                        ],
                    )
                ],
                persistence_type="session",
                persistence=True,
            )
        ]

    def _set_wrapper_callbacks(self) -> None:
        @callback(
            Output(self._plugin_unique_id.to_string(), "children"),
            Input("webviz-content-manager", "activeViewId"),
            Input("webviz-content-manager", "activePluginId"),
        )
        def change_view(view_id: str, plugin_id: str) -> Component:
            ctx = callback_context.triggered
            initial_call = (
                ctx[0]["prop_id"] == "."
                if ctx is not None
                and len(ctx) > 0
                and isinstance(ctx[0], dict)
                and "prop_id" in ctx[0].keys()
                else False
            )

            if plugin_id == self._plugin_unique_id.to_string() or initial_call:
                view = next(
                    (
                        view[1]
                        for view in self.views()
                        if view[1].unique_id() == view_id
                    ),
                    None,
                )
                if view:
                    return view.outer_layout()
            return dash.no_update

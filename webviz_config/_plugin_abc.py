from typing import Any, List, Optional, Type, Union, Dict, Callable
import io
import abc
import base64
import zipfile
import warnings
import sys
import urllib
from uuid import uuid4

import bleach
from dash.development.base_component import Component
from dash import Dash, Input, Output, State, html, callback, _callback
import dash
import jinja2
import webviz_core_components as wcc

from .webviz_plugin_subclasses import SettingsGroupABC, ViewABC

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
    TOOLBAR_BUTTONS = [
        "screenshot",
        "expand",
        "contact_person",
        "guided_tour",
        "feedback",
    ]

    # List of plugin specific assets which should be copied
    # over to the ./assets folder in the generated webviz app.
    # This is typically custom JavaScript and/or CSS files.
    # All paths in the returned ASSETS list should be absolute.
    ASSETS: list = []

    def __init__(
        self,
        app: dash.Dash,
        screenshot_filename: str = "webviz-screenshot.png",
    ) -> None:
        """If a plugin/subclass defines its own `__init__` function
        (which they usually do), they should remember to call
        ```python
        super().__init__()
        ```
        in its own `__init__` function in order to also run the parent `__init__`.
        """

        self._plugin_uuid = uuid4()
        self._screenshot_filename = screenshot_filename
        self._add_download_button = False

        self._views: List[ViewABC] = []
        self._shared_settings_groups: List[SettingsGroupABC] = []
        self._registered_ids: List[str] = []

        self._app = app
        self._active_view_id = ""

        self._set_wrapper_callbacks(app)

    def uuid(self, element: str) -> str:
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

        return f"{element}-{self._plugin_uuid}"

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

    def add_view(self, view: ViewABC, view_id: str) -> None:
        uuid = f"{self._plugin_uuid}-{view_id}"
        # pylint: disable=protected-access
        view._set_plugin_register_id_func(self._check_and_register_id)
        view._set_uuid(uuid)
        view._set_all_callbacks(self._app)
        self._views.append(view)

    def add_shared_settings_group(
        self,
        settings_group: SettingsGroupABC,
        settings_groups_id: str,
        visible_in_views: Optional[List[str]] = None,
        not_visible_in_views: Optional[List[str]] = None,
    ) -> None:
        uuid = f"{self._plugin_uuid}-{settings_groups_id}"
        # pylint: disable=protected-access
        settings_group._set_visible_in_views(
            visible_in_views if visible_in_views else []
        )
        settings_group._set_not_visible_in_views(
            not_visible_in_views if not_visible_in_views else []
        )
        settings_group._set_plugin_register_id_func(self._check_and_register_id)
        settings_group._set_uuid(uuid)
        settings_group._set_callbacks(self._app)
        self._shared_settings_groups.append(settings_group)

    @property
    def active_view_id(self) -> str:
        return self._active_view_id

    def views(self) -> List[ViewABC]:
        return self._views

    def view(self, view_id: str) -> ViewABC:
        view = next(
            (el for el in self.views() if el.uuid().split("-")[-1] == view_id), None
        )
        if view:
            return view

        raise LookupError(
            f"Invalid view id: '{view_id}. Available view ids: {[el.uuid for el in self.views()]}"
        )

    def shared_settings_groups(self) -> Optional[List[SettingsGroupABC]]:
        return self._shared_settings_groups

    def get_all_settings(self) -> List[html.Div]:
        # pylint: disable=protected-access
        settings = []
        shared_settings = self.shared_settings_groups()
        if shared_settings is not None:
            settings = [
                setting._wrapped_layout("", self._plugin_wrapper_id)
                for setting in shared_settings
            ]

        for view in self.views():
            settings.extend(
                [
                    setting._wrapped_layout(view.uuid(), self._plugin_wrapper_id)
                    for setting in view.settings_groups()
                ]
            )

        return settings

    @property
    def _plugin_wrapper_id(self) -> str:
        return f"plugin-wrapper-{self._plugin_uuid}"

    @property
    def plugin_data_output(self) -> Output:
        self._add_download_button = True
        return Output(self._plugin_wrapper_id, "download")

    @property
    def plugin_data_requested(self) -> Input:
        return Input(self._plugin_wrapper_id, "data_requested")

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
    ) -> Type[Component]:
        """This function returns (if the class constant SHOW_TOOLBAR is True,
        the plugin layout wrapped into a common webviz config plugin
        component, which provides some useful buttons like download of data,
        show data contact person and download plugin content to png.

        CSV download button will only appear if the plugin class has a property
        `csv_string` which should return the appropriate csv data as a string.

        If `TOOLBAR_BUTTONS` is empty, this functions returns the same
        dash layout as the plugin class provides directly.
        """

        buttons = self.__class__.TOOLBAR_BUTTONS.copy()

        if contact_person:
            # Sanitize the configuration user input
            for key in contact_person:
                contact_person[key] = bleach.clean(str(contact_person[key]))

        if self._add_download_button:
            buttons.append("download")

        """ if buttons or plugin_deprecation_warnings or argument_deprecation_warnings:
            # pylint: disable=no-member
            return wcc.WebvizPluginPlaceholder(
                id=self._plugin_wrapper_id,
                buttons=buttons,
                contact_person=contact_person,
                children=[self.layout],
                screenshot_filename=self._screenshot_filename,
                tour_steps=WebvizPluginABC._reformat_tour_steps(
                    self.tour_steps  # type: ignore[attr-defined]
                )
                if "guided_tour" in buttons and hasattr(self, "tour_steps")
                else [],
                deprecation_warnings=self._make_extended_deprecation_warnings(
                    plugin_deprecation_warnings, argument_deprecation_warnings
                ),
                feedback_url=self._make_feedback_url(),
            )
         """

        return wcc.WebvizPluginWrapper(
            id=self._plugin_wrapper_id,
            name=type(self).__name__,
            views=[{"id": view.uuid(), "name": view.name} for view in self.views()],
            showDownload=self._add_download_button,
            contactPerson=contact_person,
            deprecationWarnings=self._make_extended_deprecation_warnings(
                plugin_deprecation_warnings, argument_deprecation_warnings
            ),
            screenshotFilename=self._screenshot_filename,
            feedbackUrl=self._make_feedback_url(),
            tourSteps=self.tour_steps  # type: ignore[attr-defined]
            if hasattr(self, "tour_steps")
            else None,
            children=[self.views()[0].layout() if self.views() else self.layout],
            persistence_type="session",
            persistence=True,
        )

    def _set_wrapper_callbacks(self, app: Dash) -> None:
        @app.callback(
            Output(self._plugin_wrapper_id, "children"),
            Input("webviz-content-manager", "activeViewId"),
            Input("webviz-content-manager", "activePluginId"),
        )
        def change_view(view_id: str, plugin_id: str) -> Component:
            if plugin_id == self._plugin_wrapper_id:
                view = next(
                    (view for view in self.views() if view.uuid() == view_id), None
                )
                if view and self.active_view_id != view_id:
                    self._active_view_id = view.uuid()
                    return view.layout()
            return dash.no_update

    @staticmethod
    def extract_view_id(id_string: str) -> str:
        return id_string.split(":")[1]

    def callback(self, *_args, **_kwargs) -> Callable:  # type: ignore
        # Get the outputs using a Dash internal function
        output = _callback.handle_grouped_callback_args(_args, _kwargs)[0]

        view_ids: List[str] = []

        if isinstance(output, Output):
            view_ids.append(WebvizPluginABC.extract_view_id(output.component_id_str()))
        else:
            view_ids.extend(
                [
                    WebvizPluginABC.extract_view_id(el.component_id_str())
                    for el in output
                ]
            )

        def wrapper(original_callback_function: Callable) -> Callable:
            @self._app.callback(_args, _kwargs)
            def callback_wrapper(*_wrapper_args, **_wrapper_kwargs) -> Any:  # type: ignore
                results = original_callback_function(_wrapper_args, _wrapper_kwargs)
                if isinstance(results, tuple):
                    return tuple(
                        results[i]
                        if view_ids[i] == self.active_view_id
                        else dash.no_update
                        for i in range(0, len(results))
                    )
                return results if view_ids[0] == self.active_view_id else dash.no_update

            return callback_wrapper

        return wrapper

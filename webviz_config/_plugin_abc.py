import io
import abc
import base64
import zipfile
import warnings
import sys
import urllib
from uuid import uuid4
from typing import List, Optional, Type, Union, Dict

import bleach
from dash.development.base_component import Component
from dash import Input, Output
import jinja2
import webviz_core_components as wcc

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

    def __init__(self, screenshot_filename: str = "webviz-screenshot.png") -> None:
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
    @abc.abstractmethod
    def layout(self) -> Union[str, Type[Component]]:
        """This is the only required function of a Webviz plugin.
        It returns a Dash layout which by webviz-config is added to
        the main Webviz application.
        """

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
    def _reformat_tour_steps(steps: List[dict]) -> List[dict]:
        return [
            {"selector": "#" + step["id"], "content": step["content"]} for step in steps
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
    ) -> Union[str, Type[Component]]:
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

        if contact_person is None:
            contact_person = {}
        else:
            # Sanitize the configuration user input
            for key in contact_person:
                contact_person[key] = bleach.clean(str(contact_person[key]))

        if self._add_download_button:
            buttons.append("download")

        if buttons or plugin_deprecation_warnings or argument_deprecation_warnings:
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

        return self.layout

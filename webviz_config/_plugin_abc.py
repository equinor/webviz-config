import io
import abc
import base64
import zipfile
from uuid import uuid4
from typing import List, Optional, Type, Union

import bleach
from dash.development.base_component import Component
from dash.dependencies import Input, Output
import webviz_core_components as wcc


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
        "download_zip",
        "contact_person",
        "guided_tour",
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
        # pylint: disable=attribute-defined-outside-init
        # We do not have a __init__ method in this abstract base class
        self._add_download_button = True
        return Output(self._plugin_wrapper_id, "zip_base64")

    @property
    def plugin_data_requested(self) -> Input:
        return Input(self._plugin_wrapper_id, "data_requested")

    @staticmethod
    def _reformat_tour_steps(steps: List[dict]) -> List[dict]:
        return [
            {"selector": "#" + step["id"], "content": step["content"]} for step in steps
        ]

    @staticmethod
    def plugin_data_compress(content: List[dict]) -> str:
        byte_io = io.BytesIO()

        with zipfile.ZipFile(byte_io, "w") as zipped_data:
            for data in content:
                zipped_data.writestr(data["filename"], data["content"])

        byte_io.seek(0)

        return base64.b64encode(byte_io.read()).decode("ascii")

    def plugin_layout(
        self, contact_person: Optional[dict] = None
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

        if "download_zip" in buttons and not hasattr(self, "_add_download_button"):
            buttons.remove("download_zip")

        if buttons:
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
            )
        return self.layout

import io
import abc
import base64
import zipfile
import warnings
from uuid import uuid4

import bleach
from dash.dependencies import Input, Output
import webviz_core_components as wcc

warnings.simplefilter("default", DeprecationWarning)


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
    ASSETS = []

    def __init__(self):
        """If a plugin/subclass defines its own `__init__` function
        (which they usually do), they should remember to call
        ```python
        super().__init__()
        ```
        in its own `__init__` function in order to also run the parent `__init__`.
        """

        self._plugin_uuid = uuid4()

    def uuid(self, element: str):
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
    def layout(self):
        """This is the only required function of a Webviz plugin.
        It returns a Dash layout which by webviz-config is added to
        the main Webviz application.
        """

    @property
    def _plugin_wrapper_id(self):
        # pylint: disable=attribute-defined-outside-init
        # We do not have a __init__ method in this abstract base class
        if not hasattr(self, "_plugin_uuid"):
            self._plugin_uuid = uuid4()
        return f"plugin-wrapper-{self._plugin_uuid}"

    @property
    def plugin_data_output(self):
        # pylint: disable=attribute-defined-outside-init
        # We do not have a __init__ method in this abstract base class
        self._add_download_button = True
        return Output(self._plugin_wrapper_id, "zip_base64")

    @property
    def container_data_output(self):
        warnings.warn(
            ("Use 'plugin_data_output' instead of 'container_data_output'"),
            DeprecationWarning,
        )
        return self.plugin_data_output

    @property
    def plugin_data_requested(self):
        return Input(self._plugin_wrapper_id, "data_requested")

    @property
    def container_data_requested(self):
        warnings.warn(
            ("Use 'plugin_data_requested' instead of 'container_data_requested'"),
            DeprecationWarning,
        )
        return self.plugin_data_requested

    @staticmethod
    def _reformat_tour_steps(steps):
        return [
            {"selector": "#" + step["id"], "content": step["content"]} for step in steps
        ]

    @staticmethod
    def plugin_data_compress(content):
        byte_io = io.BytesIO()

        with zipfile.ZipFile(byte_io, "w") as zipped_data:
            for data in content:
                zipped_data.writestr(data["filename"], data["content"])

        byte_io.seek(0)

        return base64.b64encode(byte_io.read()).decode("ascii")

    @staticmethod
    def container_data_compress(content):
        warnings.warn(
            ("Use 'plugin_data_compress' instead of 'container_data_compress'"),
            DeprecationWarning,
        )
        return WebvizPluginABC.plugin_data_compress(content)

    def plugin_layout(self, contact_person=None):
        """This function returns (if the class constant SHOW_TOOLBAR is True,
        the plugin layout wrapped into a common webviz config plugin
        component, which provides some useful buttons like download of data,
        show data contact person and download plugin content to png.

        CSV download button will only appear if the plugin class has a property
        `csv_string` which should return the appropriate csv data as a string.

        If `TOOLBAR_BUTTONS` is empty, this functions returns the same
        dash layout as the plugin class provides directly.
        """

        if isinstance(self, WebvizContainerABC):
            warnings.warn(
                (
                    "The class name 'WebvizContainerABC' is deprecated. You "
                    "should change to 'WebvizPluginABC'. If you have a __init__ "
                    "function, you should at the same time call super().__init__(). "
                    "See https://github.com/equinor/webviz-config/pull/174 for "
                    "details. This warning will eventually "
                    "turn into an error in a future release of webviz-config."
                ),
                DeprecationWarning,
            )

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
            return wcc.WebvizPluginPlaceholder(
                id=self._plugin_wrapper_id,
                buttons=buttons,
                contact_person=contact_person,
                children=[self.layout],
                tour_steps=WebvizPluginABC._reformat_tour_steps(
                    self.tour_steps  # pylint: disable=no-member
                )
                if "guided_tour" in buttons and hasattr(self, "tour_steps")
                else [],
            )
        return self.layout


# pylint: disable=abstract-method
class WebvizContainerABC(WebvizPluginABC):
    """This class only exist during the deprecation period.
    """

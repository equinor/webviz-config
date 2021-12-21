import copy
from enum import Enum
from pathlib import Path
from typing import Optional

from dash import Dash

from ._theme_class import WebvizConfigTheme


class WebvizRunMode(Enum):
    NON_PORTABLE = 1
    PORTABLE = 2
    BUILDING_PORTABLE = 3


class WebvizInstanceInfo:
    """Contains global information regarding the running webviz app instance, exposed
    globally through WEBVIZ_INSTANCE_INFO.

    Note that this class utilizes a two-stage initialization approach which renders it
    useless until the initialize() method has been called. It is assumed that
    initialization will be done early during application execution, typically as part
    of the webviz_app.py / jinja2 template.
    """

    __slots__ = (
        "_is_initialized",
        "_dash_app",
        "_run_mode",
        "_theme",
        "_storage_folder",
    )

    def __init__(self) -> None:
        self._is_initialized: bool = False
        self._dash_app: Optional[Dash] = None
        self._run_mode: Optional[WebvizRunMode] = None
        self._theme: Optional[WebvizConfigTheme] = None
        self._storage_folder: Optional[Path] = None

    def initialize(
        self,
        dash_app: Dash,
        run_mode: WebvizRunMode,
        theme: WebvizConfigTheme,
        storage_folder: Path,
    ) -> None:
        """This function is responsible for the actual initialization of the object instance.
        None of the access methods in this class are valid until initialize() has been called.
        This function will be called as part of the webviz_app.py / jinja2 template.
        """
        if self._is_initialized:
            raise RuntimeError("Registry already initialized")

        if not isinstance(dash_app, Dash):
            raise TypeError("dash_app must be of type Dash")
        self._dash_app = dash_app

        if not isinstance(run_mode, WebvizRunMode):
            raise TypeError("run_mode must be of type WebvizRunMode")
        self._run_mode = run_mode

        if not isinstance(theme, WebvizConfigTheme):
            raise TypeError("theme must be of type WebvizConfigTheme")
        self._theme = theme

        if not isinstance(storage_folder, Path):
            raise TypeError("storage_folder must be of type Path")
        self._storage_folder = storage_folder

        self._is_initialized = True

    @property
    def dash_app(self) -> Dash:
        if not self._is_initialized or self._dash_app is None:
            raise RuntimeError("WebvizInstanceInfo is not yet initialized")

        return self._dash_app

    @property
    def run_mode(self) -> WebvizRunMode:
        if not self._is_initialized or self._run_mode is None:
            raise RuntimeError("WebvizInstanceInfo is not yet initialized")

        return self._run_mode

    @property
    def theme(self) -> WebvizConfigTheme:
        if not self._is_initialized or self._theme is None:
            raise RuntimeError("WebvizInstanceInfo is not yet initialized")

        # The theme class is mutable, so return a copy
        return copy.deepcopy(self._theme)

    @property
    def storage_folder(self) -> Path:
        if not self._is_initialized or self._storage_folder is None:
            raise RuntimeError("WebvizInstanceInfo is not yet initialized")

        return self._storage_folder


WEBVIZ_INSTANCE_INFO = WebvizInstanceInfo()

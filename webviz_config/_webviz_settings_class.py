import copy
from typing import Dict, Any, Mapping

from ._theme_class import WebvizConfigTheme


class WebvizSettings:
    """This class contains global Webviz settings that will be made available
    to all plugins through the special argument named webviz_settings.
    """

    def __init__(self, shared_settings: Dict[str, Any], theme: WebvizConfigTheme):
        if not isinstance(shared_settings, dict):
            raise TypeError("shared_settings must be of type dict")

        if not isinstance(theme, WebvizConfigTheme):
            raise TypeError("theme must be of type WebvizConfigTheme")

        self._shared_settings = shared_settings
        self._theme = theme

    @property
    def shared_settings(self) -> Mapping[str, Any]:
        return copy.deepcopy(self._shared_settings)

    @property
    def theme(self) -> WebvizConfigTheme:
        return copy.deepcopy(self._theme)

from typing import Dict, Any, Mapping

from ._theme_class import WebvizConfigTheme


class WebvizSettings:
    """This class contains global Webviz settings that will be made available
    to all plugins through the special argument named webviz_settings.
    """

    def __init__(
        self, shared_settings: Dict[str, Any], theme: WebvizConfigTheme, portable: bool
    ):
        self._shared_settings = shared_settings
        self._theme = theme
        self._portable = portable

    # TODO(Sigurd) How to type and what should we return here?
    # For typing, either Dict or Mapping
    # Do we just return our dict or should we make a copy?
    @property
    def shared_settings(self) -> Mapping[str, Any]:
        return self._shared_settings

    @property
    def theme(self) -> WebvizConfigTheme:
        return self._theme

    @property
    def portable(self) -> bool:
        return self._portable

import sys
from importlib.metadata import entry_points

from .. import WebvizConfigTheme
from ._default_theme import default_theme

installed_themes = {default_theme.theme_name: default_theme}

__all__ = ["installed_themes"]

for entry_point in (
    entry_points().get("webviz_config_themes", [])
    if sys.version_info < (3, 10, 0)
    else entry_points(  # pylint: disable=unexpected-keyword-arg
        group="webviz_config_themes"
    )
):

    theme = entry_point.load()

    globals()[entry_point.name] = theme
    __all__.append(entry_point.name)

    if isinstance(theme, WebvizConfigTheme):
        installed_themes[theme.theme_name] = theme

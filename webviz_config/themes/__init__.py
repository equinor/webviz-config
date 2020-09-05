try:
    # Python 3.8+
    from importlib.metadata import entry_points  # type: ignore
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import entry_points  # type: ignore

from .. import WebvizConfigTheme
from ._default_theme import default_theme

installed_themes = {  # pylint: disable=invalid-name
    default_theme.theme_name: default_theme
}

__all__ = ["installed_themes"]

for entry_point in entry_points().get("webviz_config_themes", []):
    theme = entry_point.load()

    globals()[entry_point.name] = theme
    __all__.append(entry_point.name)

    if isinstance(theme, WebvizConfigTheme):
        installed_themes[theme.theme_name] = theme

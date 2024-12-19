import sys
from importlib.metadata import EntryPoint, entry_points

from .. import WebvizConfigTheme
from ._default_theme import default_theme

installed_themes = {default_theme.theme_name: default_theme}

__all__ = ["installed_themes"]


def process_entry_point(entry_point: EntryPoint):
    theme = entry_point.load()

    globals()[entry_point.name] = theme
    __all__.append(entry_point.name)

    if isinstance(theme, WebvizConfigTheme):
        installed_themes[theme.theme_name] = theme


if sys.version_info < (3, 10, 0):
    eps = entry_points().get("webviz_config_themes", [])
else:
    eps = entry_points().select(group="webviz_config_themes")

for ep in eps:
    process_entry_point(ep)

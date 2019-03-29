import pkg_resources

from ._theme_class import WebvizConfigTheme
from ._default_theme import default_theme

installed_themes = {default_theme.theme_name: default_theme}

__all__ = ['WebvizConfigTheme',
           'default_theme',
           'installed_themes']

for entry_point in pkg_resources.iter_entry_points('webviz_config_themes'):
    theme = entry_point.load()

    globals()[entry_point.name] = theme
    __all__.append(entry_point.name)

    if isinstance(theme, WebvizConfigTheme):
        installed_themes[theme.theme_name] = theme

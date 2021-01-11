try:
    # Python 3.8+
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

from ._theme_class import WebvizConfigTheme
from ._webviz_settings_class import WebvizSettings
from ._localhost_token import LocalhostToken
from ._is_reload_process import is_reload_process
from ._plugin_abc import WebvizPluginABC, EncodedFile, ZipFileMember
from ._shared_settings_subscriptions import SHARED_SETTINGS_SUBSCRIPTIONS

try:
    __version__ = version("webviz-config")
except PackageNotFoundError:
    # package is not installed
    pass

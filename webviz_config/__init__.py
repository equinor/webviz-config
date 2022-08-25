from importlib.metadata import version, PackageNotFoundError

from ._theme_class import WebvizConfigTheme
from ._webviz_settings_class import WebvizSettings
from ._localhost_token import LocalhostToken
from ._is_reload_process import is_reload_process
from ._plugin_abc import WebvizPluginABC, EncodedFile, ZipFileMember
from ._shared_settings_subscriptions import SHARED_SETTINGS_SUBSCRIPTIONS
from .webviz_instance_info import WEBVIZ_INSTANCE_INFO
from ._oauth2 import Oauth2

try:
    __version__ = version("webviz-config")
except PackageNotFoundError:
    # package is not installed
    pass

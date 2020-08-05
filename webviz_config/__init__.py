from pkg_resources import get_distribution, DistributionNotFound

from ._theme_class import WebvizConfigTheme
from ._localhost_token import LocalhostToken
from ._is_reload_process import is_reload_process
from ._plugin_abc import WebvizPluginABC
from ._shared_settings_subscriptions import SHARED_SETTINGS_SUBSCRIPTIONS

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

import warnings

from pkg_resources import get_distribution, DistributionNotFound

from ._localhost_token import LocalhostToken
from ._localhost_open_browser import LocalhostOpenBrowser
from ._localhost_certificate import LocalhostCertificate
from ._is_reload_process import is_reload_process
from ._plugin_abc import WebvizPluginABC, WebvizContainerABC
from ._theme_class import WebvizConfigTheme
from ._shared_settings_subscriptions import SHARED_SETTINGS_SUBSCRIPTIONS

warnings.simplefilter("ignore", DeprecationWarning)
# See https://github.com/plotly/plotly.py/issues/2045.
# We silence this DeprecationWarning in order to not confuse the end-user.
import plotly.express  # pylint: disable=wrong-import-position,wrong-import-order

warnings.simplefilter("default", DeprecationWarning)

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

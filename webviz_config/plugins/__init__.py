"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

import warnings

try:
    # Python 3.8+
    from importlib.metadata import distributions
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import distributions  # type: ignore

from ._utils import load_webviz_plugins_with_metadata, PluginProjectMetaData


with warnings.catch_warnings():
    # As of Sep. 30th 2021, dash-bootstrap-components on PyPI
    # (https://pypi.org/project/dash-bootstrap-components/)
    # did not have a new version using dash==2.0 import statements.
    # Ignore warnings temporarily from that module in order to not
    # confuse end users.
    warnings.filterwarnings(
        "ignore", category=UserWarning, module="dash_bootstrap_components._table"
    )

    PLUGIN_METADATA, PLUGIN_PROJECT_METADATA = load_webviz_plugins_with_metadata(
        distributions(), globals()
    )

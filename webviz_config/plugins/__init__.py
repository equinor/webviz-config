"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

from typing import Optional

try:
    # Python 3.8+
    from importlib.metadata import distributions  # type: ignore
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import distributions  # type: ignore

from ._utils import load_webviz_plugins_with_metadata, PluginDistInfo


metadata = load_webviz_plugins_with_metadata(distributions(), globals())

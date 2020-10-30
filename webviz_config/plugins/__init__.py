"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

from typing import Optional
from .plugin_utils import load_webviz_plugins_with_metadata

try:
    # Python 3.8+
    # pylint: disable=ungrouped-imports
    from importlib.metadata import distributions  # type: ignore
    from typing import TypedDict  # type: ignore
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import distributions  # type: ignore
    from typing_extensions import TypedDict  # type: ignore


class PluginDistInfo(TypedDict):
    dist_name: str
    dist_version: str
    documentation_url: Optional[str]
    download_url: Optional[str]
    issue_url: Optional[str]


metadata = {}

load_webviz_plugins_with_metadata(distributions(), metadata, globals())

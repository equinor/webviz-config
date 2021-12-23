"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

try:
    # Python 3.8+
    from importlib.metadata import distributions
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import distributions  # type: ignore

from ._utils import load_webviz_plugins_with_metadata, PluginProjectMetaData


PLUGIN_METADATA, PLUGIN_PROJECT_METADATA = load_webviz_plugins_with_metadata(
    distributions(), globals()
)

"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

from importlib.metadata import distributions

from ._utils import load_webviz_plugins_with_metadata, PluginProjectMetaData


PLUGIN_METADATA, PLUGIN_PROJECT_METADATA = load_webviz_plugins_with_metadata(
    distributions(), globals()
)

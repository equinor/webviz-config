"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

import abc
from importlib.metadata import distributions

from ._utils import load_webviz_plugins_with_metadata, PluginProjectMetaData


(
    PLUGIN_METADATA,
    PLUGIN_PROJECT_METADATA,
    plugin_entrypoints,
) = load_webviz_plugins_with_metadata(distributions())

__all__ = list(plugin_entrypoints.keys())


def __getattr__(name: str) -> abc.ABC:
    """Lazy load plugins, i.e. only import/load when a given plugin is requested."""

    if name in __all__:
        return plugin_entrypoints[name].load()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

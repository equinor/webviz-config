"""Implements registry that contains all installed plugins
"""

from typing import Dict, List, Type, Callable

from .._plugin_abc import WebvizPluginABC
from ._load_all_installed_webviz_plugins import load_all_installed_webviz_plugins
from ._load_all_installed_webviz_plugins import PluginDistInfo
from ._load_all_installed_webviz_plugins import LoadedPlugin

try:
    # Python 3.8+
    from importlib.metadata import distributions  # type: ignore
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import distributions  # type: ignore

# Currently do all the imports here during module execution
# May be refactored to do lazy loading when first accessed through one of the functions below
_all_loaded_plugins: Dict[str, LoadedPlugin] = load_all_installed_webviz_plugins(
    distributions()
)


def has_plugin(plugin_name: str) -> bool:
    return plugin_name in _all_loaded_plugins


def plugin_class(plugin_name: str) -> Type[WebvizPluginABC]:
    return _all_loaded_plugins[plugin_name].plugin_class


def plugin_metadata(plugin_name: str) -> PluginDistInfo:
    return _all_loaded_plugins[plugin_name].dist_info


# Something along these lines will probably be needed for validation using pydantic
def overloaded_init_methods_for_plugin(_plugin_name: str) -> List[Callable]:
    return []


def all_plugin_names() -> List[str]:
    return list(_all_loaded_plugins)

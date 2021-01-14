"""Implements registry that contains all installed plugins
"""

from typing import Dict, List, Type, Callable

from .._plugin_abc import WebvizPluginABC
from ._load_webviz_plugins_with_metadata import load_webviz_plugins_with_metadata
from ._load_webviz_plugins_with_metadata import PluginDistInfo

try:
    # Python 3.8+
    from importlib.metadata import distributions  # type: ignore
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import distributions  # type: ignore

# Currently does all the imports here during module execution
# May be refactored when incorporating pydantic
# May also be refactored to do lazy loading when first accessed through one of the functions below
_all_installed_plugins: Dict[str, Type[WebvizPluginABC]] = {}
_all_installed_metadata = load_webviz_plugins_with_metadata(
    distributions(), _all_installed_plugins
)


def has_plugin(plugin_name: str) -> bool:
    return plugin_name in _all_installed_plugins


def plugin_class(plugin_name: str) -> Type[WebvizPluginABC]:
    return _all_installed_plugins[plugin_name]


def plugin_metadata(plugin_name: str) -> PluginDistInfo:
    return _all_installed_metadata[plugin_name]


# Something along these lines will probably be needed for validation using pydantic
def overloaded_init_methods_for_plugin(_plugin_name: str) -> List[Callable]:
    return []


def all_plugin_names() -> List[str]:
    return list(_all_installed_plugins)

import sys
import warnings
from typing import Any, Dict, Iterable, Optional, Type

from .._plugin_abc import WebvizPluginABC

# pylint: disable=no-name-in-module
if sys.version_info >= (3, 8):
    from typing import TypedDict
    from importlib.metadata import Distribution  # pylint: disable=import-error
    from importlib.metadata import EntryPoint  # pylint: disable=import-error
else:
    from typing_extensions import TypedDict
    from importlib_metadata import Distribution  # pylint: disable=import-error
    from importlib_metadata import EntryPoint  # pylint: disable=import-error


class PluginDistInfo(TypedDict):
    dist_name: str
    dist_version: str
    documentation_url: Optional[str]
    download_url: Optional[str]
    tracker_url: Optional[str]


# Candidate for dataclass once we're past python 3.6
# pylint: disable=too-few-public-methods
class DiscoveredPlugin:
    def __init__(self, entry_point: EntryPoint, dist_info: PluginDistInfo) -> None:
        self.entry_point = entry_point
        self.dist_info = dist_info


# Candidate for dataclass once we're past python 3.6
# pylint: disable=too-few-public-methods
class LoadedPlugin:
    def __init__(
        self, plugin_class: Type[WebvizPluginABC], dist_info: PluginDistInfo
    ) -> None:
        self.plugin_class = plugin_class
        self.dist_info = dist_info


def _discover_all_installed_webviz_plugin_entry_points(
    distributions: Iterable[Distribution],
) -> Dict[str, DiscoveredPlugin]:
    """Iterates over the given distributions and finds all entry points corresponding
    to webviz plugins. Also captures dist info for the discovered plugins
    """
    discovered_plugins: Dict[str, DiscoveredPlugin] = {}

    for dist in distributions:
        for entry_point in dist.entry_points:
            if entry_point.group == "webviz_config_plugins":
                project_urls = {
                    value.split(",")[0]: value.split(",")[1].strip()
                    for (key, value) in dist.metadata.items()
                    if key == "Project-URL"
                }

                if entry_point.name in discovered_plugins:
                    existing_dist_info = discovered_plugins[entry_point.name].dist_info
                    warnings.warn(
                        f"Multiple versions of plugin with name {entry_point.name}. "
                        f"Already found in project {existing_dist_info['dist_name']}. "
                        f"Overwriting using plugin from project {dist.metadata['name']}",
                        RuntimeWarning,
                    )

                dist_info: PluginDistInfo = {
                    "dist_name": dist.metadata["name"],
                    "dist_version": dist.version,
                    "documentation_url": project_urls.get("Documentation"),
                    "download_url": project_urls.get("Download"),
                    "tracker_url": project_urls.get("Tracker"),
                }

                discovered_plugins[entry_point.name] = DiscoveredPlugin(
                    entry_point, dist_info
                )

    return discovered_plugins


def _is_legal_webviz_plugin_class(obj: Any) -> bool:
    return issubclass(obj, WebvizPluginABC) and obj is not WebvizPluginABC


def load_all_installed_webviz_plugins(
    distributions: Iterable[Distribution],
) -> Dict[str, LoadedPlugin]:
    """Iterates over the given distributions, finds all entry points corresponding
    to webviz-config plugins, and then loads all the plugins
    """

    all_discovered_plugins = _discover_all_installed_webviz_plugin_entry_points(
        distributions
    )
    loaded_plugins: Dict[str, LoadedPlugin] = {}
    for plugin_name, discovered_plugin in all_discovered_plugins.items():

        loaded_class_reference = discovered_plugin.entry_point.load()

        # Check that this is actually a plugin that inherits from WebvizPluginABC,
        # and if not, make sure we don't add it.
        if not _is_legal_webviz_plugin_class(loaded_class_reference):
            warnings.warn(
                f"Plugin with name {plugin_name} is not a valid subclass of "
                f"WebvizPluginABC. The plugin will be ignored and will not be available.",
                RuntimeWarning,
            )
            continue

        loaded_plugins[plugin_name] = LoadedPlugin(
            loaded_class_reference, discovered_plugin.dist_info
        )

    return loaded_plugins

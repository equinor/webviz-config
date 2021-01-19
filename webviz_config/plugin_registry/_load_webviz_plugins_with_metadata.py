import sys
import warnings
from typing import Any, Dict, Iterable, Optional, Type

from .._plugin_abc import WebvizPluginABC

# pylint: disable=no-name-in-module
if sys.version_info >= (3, 8):
    from typing import TypedDict
    from importlib.metadata import Distribution  # pylint: disable=import-error
else:
    from typing_extensions import TypedDict
    from importlib_metadata import Distribution  # pylint: disable=import-error


class PluginDistInfo(TypedDict):
    dist_name: str
    dist_version: str
    documentation_url: Optional[str]
    download_url: Optional[str]
    tracker_url: Optional[str]


def load_webviz_plugins_with_metadata(
    distributions: Iterable[Distribution],
    loaded_plugins: Dict[str, Type[WebvizPluginABC]],
) -> Dict[str, PluginDistInfo]:
    """Loads the given distributions, finds entry points corresponding to webviz-config
    plugins, and put them into the mutable input dictionary loaded_plugins
    (key is plugin name string, value is reference to plugin class).
    Also returns a dictionary of plugin metadata.
    """

    metadata: Dict[str, PluginDistInfo] = {}

    for dist in distributions:
        for entry_point in dist.entry_points:
            if entry_point.group == "webviz_config_plugins":
                project_urls = {
                    value.split(",")[0]: value.split(",")[1].strip()
                    for (key, value) in dist.metadata.items()
                    if key == "Project-URL"
                }

                if entry_point.name in metadata:
                    warnings.warn(
                        f"Multiple versions of plugin with name {entry_point.name}. "
                        f"Already loaded from project {metadata[entry_point.name]['dist_name']}. "
                        f"Overwriting using plugin from project {dist.metadata['name']}",
                        RuntimeWarning,
                    )

                loaded_class_reference = entry_point.load()

                # Check that this is actually a plugin that inherits from WebvizPluginABC,
                # and if not, make sure we don't add it.
                if not _is_legal_webviz_plugin_class(loaded_class_reference):
                    warnings.warn(
                        f"Plugin with name {entry_point.name} is not a valid subclass of "
                        f"WebvizPluginABC. The plugin will be ignored and will not be available.",
                        RuntimeWarning,
                    )
                    continue

                loaded_plugins[entry_point.name] = loaded_class_reference

                metadata[entry_point.name] = {
                    "dist_name": dist.metadata["name"],
                    "dist_version": dist.version,
                    "documentation_url": project_urls.get("Documentation"),
                    "download_url": project_urls.get("Download"),
                    "tracker_url": project_urls.get("Tracker"),
                }

    return metadata


def _is_legal_webviz_plugin_class(obj: Any) -> bool:
    return issubclass(obj, WebvizPluginABC) and obj is not WebvizPluginABC

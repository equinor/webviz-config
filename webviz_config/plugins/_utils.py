import warnings
from typing import Any, Dict, Iterable, Optional

try:
    # Python 3.8+
    # pylint: disable=ungrouped-imports
    from typing import TypedDict  # type: ignore
except ImportError:
    # Python < 3.8
    from typing_extensions import TypedDict  # type: ignore


class PluginDistInfo(TypedDict):
    dist_name: str
    dist_version: str
    documentation_url: Optional[str]
    download_url: Optional[str]
    tracker_url: Optional[str]


def load_webviz_plugins_with_metadata(
    distributions: Iterable, loaded_plugins: Dict[str, Any]
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
                        f"Overwriting using plugin with from project {dist.metadata['name']}",
                        RuntimeWarning,
                    )

                metadata[entry_point.name] = {
                    "dist_name": dist.metadata["name"],
                    "dist_version": dist.version,
                    "documentation_url": project_urls.get("Documentation"),
                    "download_url": project_urls.get("Download"),
                    "tracker_url": project_urls.get("Tracker"),
                }

                loaded_plugins[entry_point.name] = entry_point.load()

    return metadata

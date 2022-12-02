import re
import warnings
from typing import Dict, Iterable, Optional, Tuple, TypedDict

from importlib.metadata import requires, version, PackageNotFoundError, EntryPoint


class PluginProjectMetaData(TypedDict):
    dist_version: str
    dependencies: Dict[str, str]
    documentation_url: Optional[str]
    download_url: Optional[str]
    source_url: Optional[str]
    tracker_url: Optional[str]


def _plugin_dist_dependencies(plugin_dist_name: str) -> Dict[str, str]:
    """Returns overview of all dependencies (indirect + direct) of a given
    plugin project installed in the current environment.

    Key is package name of dependency, value is (installed) version string.
    """

    untraversed_dependencies = set([plugin_dist_name])
    requirements = {}

    while untraversed_dependencies:
        sub_dependencies = requires(untraversed_dependencies.pop())

        if sub_dependencies is None:
            continue

        for sub_dependency in sub_dependencies:
            split = re.split(r"[;<>~=()]", sub_dependency, 1)
            package_name = split[0].strip().replace("_", "-").lower()

            if package_name not in requirements:
                # Only include package in dependency list
                # if it is not an "extra" dependency...
                if len(split) == 1 or "extra" not in split[1]:
                    try:
                        # ...and if it is actually installed (there are dependencies
                        # in setup.py that e.g. are not installed on certain Python
                        # versions and operating system combinations).
                        requirements[package_name] = version(package_name)
                        untraversed_dependencies.add(package_name)
                    except PackageNotFoundError:
                        pass

    return {k: requirements[k] for k in sorted(requirements)}


def load_webviz_plugins_with_metadata(
    distributions: Iterable,
) -> Tuple[Dict[str, dict], Dict[str, PluginProjectMetaData], Dict[str, EntryPoint]]:
    """Finds entry points corresponding to webviz-config plugins,
    and returns them as a dictionary (key is plugin name string,
    value is reference to entrypoint).

    Also returns a dictionary of plugin metadata.
    """

    plugin_project_metadata: Dict[str, PluginProjectMetaData] = {}
    plugin_metadata: Dict[str, dict] = {}
    plugin_entrypoints: Dict[str, EntryPoint] = {}

    for dist in distributions:
        for entry_point in dist.entry_points:
            if entry_point.group == "webviz_config_plugins":
                dist_name = dist.metadata["name"]

                if (
                    entry_point.name in plugin_metadata
                    and dist_name not in plugin_project_metadata
                ):
                    warnings.warn(
                        f"Multiple versions of plugin with name {entry_point.name}. Already "
                        f"loaded from project {plugin_metadata[entry_point.name]['dist_name']}. "
                        f"Overwriting using plugin with from project {dist_name}",
                        RuntimeWarning,
                    )

                if dist_name not in plugin_project_metadata:
                    project_urls = {
                        value.split(",")[0]: value.split(",")[1].strip()
                        for (key, value) in dist.metadata.items()
                        if key == "Project-URL"
                    }

                    plugin_project_metadata[dist_name] = PluginProjectMetaData(
                        {
                            "dist_version": dist.version,
                            "dependencies": _plugin_dist_dependencies(dist_name),
                            "documentation_url": project_urls.get("Documentation"),
                            "download_url": project_urls.get("Download"),
                            "source_url": project_urls.get("Source"),
                            "tracker_url": project_urls.get("Tracker"),
                        }
                    )

                plugin_metadata[entry_point.name] = {
                    "dist_name": dist.metadata["name"],
                }

                plugin_entrypoints[entry_point.name] = entry_point

    return (plugin_metadata, plugin_project_metadata, plugin_entrypoints)

"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

import inspect
from typing import Optional

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

for dist in distributions():
    for entry_point in dist.entry_points:
        if entry_point.group == "webviz_config_plugins":
            project_urls = {
                value.split(",")[0]: value.split(",")[1].strip()
                for (key, value) in dist.metadata.items()
                if key == "Project-URL"
            }

            metadata[entry_point.name] = {
                "dist_name": dist.metadata["name"],
                "dist_version": dist.version,
                "documentation_url": project_urls.get("Documentation"),
                "download_url": project_urls.get("Download"),
                "tracker_url": project_urls.get("Tracker"),
            }

            globals()[entry_point.name] = entry_point.load()

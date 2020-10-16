import warnings

def write_metadata(distributions, metadata):
    for dist in distributions:
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

                if entry_point.name in globals():
                    warning_string = f"Plugin {entry_point.name} already exists. Overwriting."
                    warnings.warn(warning_string, RuntimeWarning)

                globals()[entry_point.name] = entry_point.load()

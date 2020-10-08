"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

try:
    # Python 3.8+
    from importlib.metadata import entry_points  # type: ignore
except ModuleNotFoundError:
    # Python < 3.8
    from importlib_metadata import entry_points  # type: ignore

__all__ = []

for entry_point in entry_points().get("webviz_config_plugins", []):
    globals()[entry_point.name] = entry_point.load()
    __all__.append(entry_point.name)

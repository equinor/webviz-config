import warnings

import mock

from webviz_config.plugin_registry._load_all_installed_webviz_plugins import (
    _discover_all_installed_webviz_plugin_entry_points,
)


class DistMock:
    # pylint: disable=too-few-public-methods
    def __init__(self, entry_points, name):
        self.metadata = {"name": name}

        self.entry_points = entry_points
        self.version = "123"


plugin_entrypoint_mock1 = mock.Mock()
plugin_entrypoint_mock1.group = "webviz_config_plugins"
plugin_entrypoint_mock1.name = "SomePlugin1"

plugin_entrypoint_mock2 = mock.Mock()
plugin_entrypoint_mock2.group = "webviz_config_plugins"
plugin_entrypoint_mock2.name = "SomePlugin2"

dist_mock1 = DistMock([plugin_entrypoint_mock1], "dist_mock1")
dist_mock2 = DistMock([plugin_entrypoint_mock1], "dist_mock2")
dist_mock3 = DistMock([plugin_entrypoint_mock2], "dist_mock3")


def test_no_warning():
    with warnings.catch_warnings(record=True) as warn:
        discovered_plugins = _discover_all_installed_webviz_plugin_entry_points(
            [dist_mock1, dist_mock3]
        )
        assert len(warn) == 0, "Too many warnings"

    assert len(discovered_plugins) == 2, "Wrong number of items in discovered_plugins"
    assert "SomePlugin1" in discovered_plugins
    assert "SomePlugin2" in discovered_plugins


def test_warning_multiple():
    with warnings.catch_warnings(record=True) as warn:
        discovered_plugins = _discover_all_installed_webviz_plugin_entry_points(
            [dist_mock1, dist_mock2]
        )

        assert len(warn) == 1
        assert issubclass(warn[-1].category, RuntimeWarning)
        assert str(warn[-1].message) == (
            "Multiple versions of plugin with name SomePlugin1. "
            "Already found in project dist_mock1. "
            "Overwriting using plugin from project dist_mock2"
        )

    assert len(discovered_plugins) == 1, "Wrong number of items in discovered_plugins"
    assert "SomePlugin1" in discovered_plugins
    assert (
        discovered_plugins["SomePlugin1"].dist_info["dist_name"] == "dist_mock2"
    ), "Wrong dist name"

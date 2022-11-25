import warnings
from unittest import mock
import importlib
import importlib.metadata

import webviz_config.plugins._utils


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


def test_no_warning(monkeypatch):
    # pylint: disable=protected-access
    monkeypatch.setattr(importlib.metadata, "requires", lambda x: [])
    importlib.reload(webviz_config.plugins._utils)

    with warnings.catch_warnings(record=True) as warn:
        (
            metadata,
            _,
            plugin_entrypoints,
        ) = webviz_config.plugins._utils.load_webviz_plugins_with_metadata(
            [dist_mock1, dist_mock3]
        )
        assert len(warn) == 0, "Too many warnings"

    assert len(metadata) == 2, "Wrong number of items in metadata"
    assert "SomePlugin1" in plugin_entrypoints
    assert "SomePlugin2" in plugin_entrypoints


def test_warning_multiple(monkeypatch):
    # pylint: disable=protected-access
    monkeypatch.setattr(importlib.metadata, "requires", lambda x: [])
    importlib.reload(webviz_config.plugins._utils)

    with warnings.catch_warnings(record=True) as warn:
        (
            metadata,
            _,
            plugin_entrypoints,
        ) = webviz_config.plugins._utils.load_webviz_plugins_with_metadata(
            [dist_mock1, dist_mock2]
        )

        assert len(warn) == 1
        assert issubclass(warn[-1].category, RuntimeWarning)
        print(warn[-1].message)
        assert str(warn[-1].message) == (
            "Multiple versions of plugin with name SomePlugin1. "
            "Already loaded from project dist_mock1. "
            "Overwriting using plugin with from project dist_mock2"
        )

    assert len(metadata) == 1, "Wrong number of items in metadata"
    assert metadata["SomePlugin1"]["dist_name"] == "dist_mock2", "Wrong dist name"
    assert "SomePlugin1" in plugin_entrypoints

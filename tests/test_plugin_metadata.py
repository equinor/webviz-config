import webviz_config
from webviz_config import plugin_registry


def test_webviz_config_metadata():
    meta = plugin_registry.plugin_metadata("BannerImage")

    assert meta["dist_name"] == "webviz-config"
    assert meta["dist_version"] == webviz_config.__version__

    assert meta["documentation_url"] == "https://equinor.github.io/webviz-config"
    assert meta["download_url"] == "https://pypi.org/project/webviz-config"
    assert meta["tracker_url"] == "https://github.com/equinor/webviz-config/issues"

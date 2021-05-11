import webviz_config
from webviz_config.plugins import PLUGIN_PROJECT_METADATA


def test_webviz_config_metadata():

    metadata = PLUGIN_PROJECT_METADATA["webviz-config"]

    assert metadata["dist_version"] == webviz_config.__version__
    assert metadata["documentation_url"] == "https://equinor.github.io/webviz-config"
    assert metadata["download_url"] == "https://pypi.org/project/webviz-config"
    assert metadata["source_url"] == "https://github.com/equinor/webviz-config"
    assert metadata["tracker_url"] == "https://github.com/equinor/webviz-config/issues"

    assert "dash" in metadata["dependencies"]  # dash is a direct dependency
    assert "flask" in metadata["dependencies"]  # flask is an indirect dependency

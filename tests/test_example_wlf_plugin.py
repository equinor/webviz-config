from webviz_config.testing import WebvizComposite
from webviz_config.generic_plugins._example_wlf_plugin import ExampleWlfPlugin


def test_example_wlf_plugin(
    _webviz_duo: WebvizComposite,
) -> None:

    plugin = ExampleWlfPlugin(title="hello")

    _webviz_duo.start_server(plugin)

    _webviz_duo.toggle_webviz_settings_drawer()

    _webviz_duo.toggle_webviz_settings_group(
        plugin.view("plot-view").settings_group_unique_id("plot-settings")
    )

    component_id = _webviz_duo.view_settings_group_unique_component_id(
        view_id="plot-view",
        settings_group_id="plot-settings",
        component_unique_id="coordinates-selector",
    )

    _webviz_duo.wait_for_contains_text(component_id, "x - y")
    assert _webviz_duo.get_logs() == []

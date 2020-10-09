import dash

from webviz_config.common_cache import CACHE
from webviz_config.generic_plugins import _example_plugin


def test_example_plugin(dash_duo):

    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True
    CACHE.init_app(app.server)
    title = "Example"
    page = _example_plugin.ExamplePlugin(app, title)
    app.layout = page.layout
    dash_duo.start_server(app)
    btn = dash_duo.find_element("#" + page.uuid("submit-button"))
    assert btn.text == "Submit"
    text = dash_duo.find_element("#" + page.uuid("output-state"))
    assert text.text == "Button has been pressed 0 times."
    btn.click()
    dash_duo.wait_for_contains_text(
        "#" + page.uuid("output-state"), "Button has been pressed 1 times", timeout=2
    )
    assert text.text == "Button has been pressed 1 times."

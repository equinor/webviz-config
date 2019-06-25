import dash
from webviz_config.common_cache import cache
from webviz_config.containers import _example_container


def test_example_container(dash_duo):

    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True
    cache.init_app(app.server)
    title = 'Example'
    page = _example_container.ExampleContainer(app, title)
    app.layout = page.layout
    dash_duo.start_server(app)
    btn = dash_duo.find_element(f'#{page.button_id}')
    assert 'Submit' == btn.text
    text = dash_duo.find_element(f'#{page.div_id}')
    assert 'Button has been pressed 0 times.' == text.text
    btn.click()
    dash_duo.wait_for_contains_text(f'#{page.div_id}',
                                    'Button has been pressed 1 times',
                                    timeout=2)
    assert 'Button has been pressed 1 times.' == text.text

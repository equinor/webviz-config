import dash
from webviz_config.common_cache import cache
from pytest_dash.wait_for import (
    wait_for_element_by_css_selector as css_select
)
from webviz_config.containers import _example_container


def test_example_container(dash_threaded):

    app = dash.Dash(__name__)
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.config.suppress_callback_exceptions = True
    cache.init_app(app.server)
    driver = dash_threaded.driver
    title = 'Example'
    page = _example_container.ExampleContainer(app, title)
    app.layout = page.layout
    dash_threaded(app)
    btn = css_select(driver, f'#{page.button_id}')
    assert 'Submit' == btn.text
    text = css_select(driver, f'#{page.div_id}')
    assert 'Button has been pressed 0 times.' == text.text
    btn.click()
    assert 'Button has been pressed 1 times.' == text.text

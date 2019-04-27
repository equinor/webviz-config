import time
import dash
from webviz_config.common_cache import cache
from pytest_dash.wait_for import (
    wait_for_element_by_css_selector as css_select
)
from webviz_config.containers import _table_plotter


def test_table_plotter(dash_threaded):

    app = dash.Dash(__name__)
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.config.suppress_callback_exceptions = True
    cache.init_app(app.server)
    driver = dash_threaded.driver
    title = 'Example'
    csv_file = './tests/data/example_data.csv'
    page = _table_plotter.TablePlotter(app, title, csv_file)
    app.layout = page.layout
    dash_threaded(app)

    # Wait for the app to render(there is probably a better way...)
    time.sleep(5)

    # Checking that no plot options are defined
    assert page.plot_options == {}

    # Checking that the selectors are not hidden
    selector_row = css_select(driver, f'#{page.selector_row}')
    assert selector_row.get_attribute('style') == ''

    # Checking that the correct plot type is initialized
    plot_dd = css_select(driver, f'#{page.plot_option_id}-plottype')
    assert plot_dd.text == 'scatter'

    # Checking that only the relevant options are shown
    for plot_option in page.plot_args.keys():
        plot_option_dd = css_select(
            driver, f'#{page.plot_option_id}-div-{plot_option}')
        if plot_option not in page.plots['scatter']:
            assert plot_option_dd.get_attribute('style') == 'display: none;'
        else:
            assert plot_option_dd.get_attribute('style') == 'display: grid;'

    # Checking that options are initialized correctly
    for option in ['x', 'y']:
        plot_option_dd = css_select(driver, f'#{page.plot_option_id}-{option}')
        assert plot_option_dd.text == 'Well'


def test_initialized_table_plotter(dash_threaded):

    app = dash.Dash(__name__)
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.config.suppress_callback_exceptions = True
    cache.init_app(app.server)
    driver = dash_threaded.driver
    title = 'Example'
    csv_file = './tests/data/example_data.csv'
    plot_options = dict(
        x='Well',
        y='Initial reservoir pressure (bar)',
        size='Average permeability (D)',
        facet_col='Segment')

    page = _table_plotter.TablePlotter(
        app, title, csv_file, lock=True, plot_options=plot_options)
    app.layout = page.layout
    dash_threaded(app)

    # Wait for the app to render(there is probably a better way...)
    time.sleep(5)

    # Checking that plot options are defined
    assert page.plot_options == plot_options
    assert page.lock

    # Checking that the selectors are hidden
    selector_row = css_select(driver, f'#{page.selector_row}')
    assert selector_row.get_attribute('style') == 'display: none;'

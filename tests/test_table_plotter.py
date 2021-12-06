import time
from pathlib import Path

import dash
from dash.testing.composite import DashComposite

from webviz_config import WebvizSettings
from webviz_config.common_cache import CACHE
from webviz_config.themes import default_theme
from webviz_config.generic_plugins import _table_plotter


def test_table_plotter(dash_duo: DashComposite) -> None:

    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True
    CACHE.init_app(app.server)
    webviz_settings = WebvizSettings({}, default_theme)
    csv_file = Path("./tests/data/example_data.csv")
    page = _table_plotter.TablePlotter(app, webviz_settings, csv_file)
    app.layout = page.layout
    dash_duo.start_server(app)

    # Wait for the app to render(there is probably a better way...)
    time.sleep(5)

    # Checking that no plot options are defined
    assert not page.plot_options
    # Check that filter is not active
    assert not page.use_filter

    # Checking that the correct plot type is initialized
    plot_dd = dash_duo.find_element("#" + page.uuid("plottype"))
    assert plot_dd.text == "scatter"

    # Checking that only the relevant options are shown
    for plot_option in page.plot_args.keys():
        plot_option_dd = dash_duo.find_element("#" + page.uuid(f"div-{plot_option}"))
        if plot_option not in page.plots["scatter"]:
            assert plot_option_dd.get_attribute("style") == "display: none;"

    # Checking that options are initialized correctly
    for option in ["x", "y"]:
        plot_option_dd = dash_duo.find_element("#" + page.uuid(f"dropdown-{option}"))
        assert plot_option_dd.text == "Well"


def test_table_plotter_filter(dash_duo: DashComposite) -> None:

    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True
    CACHE.init_app(app.server)
    webviz_settings = WebvizSettings({}, default_theme)
    csv_file = Path("./tests/data/example_data.csv")
    page = _table_plotter.TablePlotter(
        app, webviz_settings, csv_file, filter_cols=["Well"]
    )
    app.layout = page.layout
    dash_duo.start_server(app)

    # Wait for the app to render(there is probably a better way...)
    time.sleep(5)

    # Checking that no plot options are defined
    assert not page.plot_options
    # Check that filter is active
    assert page.use_filter
    assert page.filter_cols == ["Well"]

    # Checking that the correct plot type is initialized
    plot_dd = dash_duo.find_element("#" + page.uuid("plottype"))
    assert plot_dd.text == "scatter"

    # Checking that only the relevant options are shown
    for plot_option in page.plot_args.keys():
        plot_option_dd = dash_duo.find_element("#" + page.uuid(f"div-{plot_option}"))
        if plot_option not in page.plots["scatter"]:
            assert "display: none;" in plot_option_dd.get_attribute("style")

    # Checking that options are initialized correctly
    for option in ["x", "y"]:
        plot_option_dd = dash_duo.find_element("#" + page.uuid(f"dropdown-{option}"))
        assert plot_option_dd.text == "Well"


def test_initialized_table_plotter(dash_duo: DashComposite) -> None:

    app = dash.Dash(__name__)
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.config.suppress_callback_exceptions = True
    CACHE.init_app(app.server)
    webviz_settings = WebvizSettings({}, default_theme)
    csv_file = Path("./tests/data/example_data.csv")
    plot_options = dict(
        x="Well",
        y="Initial reservoir pressure (bar)",
        size="Average permeability (D)",
        facet_col="Segment",
    )

    page = _table_plotter.TablePlotter(
        app, webviz_settings, csv_file, lock=True, plot_options=plot_options
    )
    app.layout = page.layout
    dash_duo.start_server(app)

    # Wait for the app to render(there is probably a better way...)

    # Checking that plot options are defined
    assert page.plot_options == plot_options
    assert page.lock

    # Checking that the selectors are hidden
    selector_row = dash_duo.find_element("#" + page.uuid("selector-row"))
    assert "display: none;" in selector_row.get_attribute("style")

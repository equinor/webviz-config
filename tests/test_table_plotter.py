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

    plugin = TablePlotter(app, csv_file=CSV_FILE)
    app.layout = plugin.layout
    dash_duo.start_server(app)

    # Checking that no plot options are defined
    assert plugin.plot_options == {}

    # Check that filter is not active
    assert not plugin.use_filter

    # Checking that the correct plot type is initialized
    plot_dd = dash_duo.find_element("#" + plugin.uuid("plottype"))
    assert plot_dd.text == "scatter"

    # Checking that only the relevant options are shown
    for plot_option in plugin.plot_args.keys():
        if plot_option not in plugin.plots["scatter"]:
            dash_duo.find_element("#" + plugin.uuid(f"div-{plot_option}"))
            dash_duo.wait_for_style_to_equal(
                "#" + plugin.uuid(f"div-{plot_option}"), style="display", val="none"
            )

    # Checking that options are initialized correctly
    for option in ["x", "y"]:
        plot_option_dd = dash_duo.find_element("#" + plugin.uuid(f"dropdown-{option}"))
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

    dash_duo.start_server(app)

    # Checking that no plot options are defined
    assert plugin.plot_options == {}

    # Check that filter is active
    assert plugin.use_filter
    assert plugin.filter_cols == ["Well"]

    # Checking that the correct plot type is initialized
    plot_dd = dash_duo.find_element("#" + plugin.uuid("plottype"))
    assert plot_dd.text == "scatter"

    # Checking that only the relevant options are shown
    for plot_option in plugin.plot_args.keys():
        if plot_option not in plugin.plots["scatter"]:
            dash_duo.find_element("#" + plugin.uuid(f"div-{plot_option}"))
            dash_duo.wait_for_style_to_equal(
                "#" + plugin.uuid(f"div-{plot_option}"), style="display", val="none"
            )

    # Checking that options are initialized correctly
    for option in ["x", "y"]:
        plot_option_dd = dash_duo.find_element("#" + plugin.uuid(f"dropdown-{option}"))
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

    plot_options = {
        "x": "Well",
        "y": "Initial reservoir pressure (bar)",
        "size": "Average permeability (D)",
        "facet_col": "Segment",
    }

    plugin = TablePlotter(app, csv_file=CSV_FILE, lock=True, plot_options=plot_options)
    app.layout = plugin.layout

    dash_duo.start_server(app)

    # Checking that plot options are defined
    assert plugin.plot_options == plot_options
    assert plugin.lock

    # Checking that the selectors are hidden
    selector_row = dash_duo.find_element("#" + plugin.uuid("selector-row"))
    assert "display: none;" in selector_row.get_attribute("style")

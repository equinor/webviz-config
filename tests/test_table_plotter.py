from webviz_config.plugins import TablePlotter

CSV_FILE = "./tests/data/example_data.csv"


def test_table_plotter(webviz_single_plugin, dash_duo):

    webviz_single_plugin.check_portability()

    app = webviz_single_plugin.app

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


def test_table_plotter_filter(webviz_single_plugin, dash_duo):

    app = webviz_single_plugin.app

    plugin = TablePlotter(app, csv_file=CSV_FILE, filter_cols=["Well"])
    app.layout = plugin.layout

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


def test_initialized_table_plotter(webviz_single_plugin, dash_duo):

    app = webviz_single_plugin.app

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

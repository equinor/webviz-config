from pathlib import Path
from unittest import mock

import dash

from webviz_config import WebvizConfigTheme
from webviz_config.common_cache import CACHE
from webviz_config.themes import default_theme
from webviz_config.generic_plugins import _syntax_highlighter


def test_create_themed_layout():
    # Make an instance of the theme class
    test_theme = WebvizConfigTheme(theme_name="test")
    # Add a plotly theme to the new theme
    test_theme.plotly_theme = {
        "layout": {
            "font": {"family": "Arial"},
            "colorscale": {
                "diverging": [
                    [0, "rgb(255, 0, 0)"],
                    [0.5, "rgb(255, 255, 0)"],
                    [1, "rgb(255, 255, 255)"],
                ],
                "sequential": [
                    [0, "rgb(0, 0, 255)"],
                    [0.5, "rgb(0, 255, 0)"],
                    [1, "rgb(255, 0, 0)"],
                ],
            },
            "xaxis": {"title": {"text": "Hi", "font": {"size": 10}}},
            "yaxis2": {"color": "#000"},
        },
    }
    # Define a layout that should be themed
    test_layout = {
        "font": {"size": 12},
        "colorscale": {
            "sequential": [
                [0, "rgb(0, 0, 0)"],
                [0.25, "rgb(255, 0, 0)"],
                [0.5, "rgb(0, 255, 0)"],
                [0.75, "rgb(0, 0, 255)"],
                [1, "rgb(255, 255, 255)"],
            ],
        },
        "xaxis": {"title": {"text": "New", "standoff": 2}, "type": "log"},
        "xaxis2": {},
        "yaxis": {"color": "#111"},
    }
    # The expected layout after theming is applied
    expected_themed_layout = {
        "font": {"family": "Arial", "size": 12},
        "colorscale": {
            "diverging": [
                [0, "rgb(255, 0, 0)"],
                [0.5, "rgb(255, 255, 0)"],
                [1, "rgb(255, 255, 255)"],
            ],
            "sequential": [
                [0, "rgb(0, 0, 0)"],
                [0.25, "rgb(255, 0, 0)"],
                [0.5, "rgb(0, 255, 0)"],
                [0.75, "rgb(0, 0, 255)"],
                [1, "rgb(255, 255, 255)"],
            ],
        },
        "xaxis": {
            "title": {"text": "New", "font": {"size": 10}, "standoff": 2},
            "type": "log",
        },
        "xaxis2": {"title": {"text": "Hi", "font": {"size": 10}}},
        "yaxis": {"color": "#111"},
        "yaxis2": {"color": "#000"},
    }

    # Make a themed layout using the create_themed_layout method
    themed_layout = test_theme.create_themed_layout(test_layout)

    # Verify that the themed layout is as expected
    assert themed_layout == expected_themed_layout

    # Verify that the theme layout is unchanged (same as when set)
    assert test_theme.plotly_theme == {
        "layout": {
            "font": {"family": "Arial"},
            "colorscale": {
                "diverging": [
                    [0, "rgb(255, 0, 0)"],
                    [0.5, "rgb(255, 255, 0)"],
                    [1, "rgb(255, 255, 255)"],
                ],
                "sequential": [
                    [0, "rgb(0, 0, 255)"],
                    [0.5, "rgb(0, 255, 0)"],
                    [1, "rgb(255, 0, 0)"],
                ],
            },
            "yaxis2": {"color": "#000"},
            "xaxis": {"title": {"text": "Hi", "font": {"size": 10}}},
        },
    }

    # Verify that the test_layout unchanged (same as when set)
    assert test_layout == {
        "font": {"size": 12},
        "colorscale": {
            "sequential": [
                [0, "rgb(0, 0, 0)"],
                [0.25, "rgb(255, 0, 0)"],
                [0.5, "rgb(0, 255, 0)"],
                [0.75, "rgb(0, 0, 255)"],
                [1, "rgb(255, 255, 255)"],
            ],
        },
        "xaxis": {"title": {"text": "New", "standoff": 2}, "type": "log"},
        "yaxis": {"color": "#111"},
        "xaxis2": {},
    }


def test_create_themed_layout_on_app(dash_duo):
    # Test themed with a running app
    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True
    CACHE.init_app(app.server)
    code_file = Path("./tests/data/basic_example.yaml")
    with mock.patch(
        "webviz_config.generic_plugins._syntax_highlighter.get_path"
    ) as mock_path:
        mock_path.return_value = code_file
        page = _syntax_highlighter.SyntaxHighlighter(app, code_file)
        app.layout = page.layout
        dash_duo.start_server(app)
        # empty input dict should return the theme layout
        assert default_theme.plotly_theme[
            "layout"
        ] == default_theme.create_themed_layout({})
        # empty input dict should return the theme layout
        specified_layout = {
            "colorway": ["#FFFFFF", "#0000FF"],
            "xaxis": {"title": {"text": "Title"}, "type": "log", "constrain": "domain"},
            "legend": {"font": {"family": "Arial"}},
        }
        # create a new layout from specified and theme layouts
        new_layout = default_theme.create_themed_layout(specified_layout)
        # test some values
        assert new_layout["colorway"] == specified_layout["colorway"]
        assert new_layout["xaxis"]["title"]["text"] == "Title"
        assert dash_duo.get_logs() == [], "browser console should contain no error"

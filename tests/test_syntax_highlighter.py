from pathlib import Path
from unittest import mock

import dash

from webviz_config.common_cache import CACHE
from webviz_config.generic_plugins import _syntax_highlighter


def test_syntax_highlighter(dash_duo):

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
        assert dash_duo.get_logs() == [], "browser console should contain no error"

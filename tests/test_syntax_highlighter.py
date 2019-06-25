import mock
from pathlib import Path
import dash
from webviz_config.common_cache import cache
from webviz_config.containers import _syntax_highlighter

# mocked functions
get_path = 'webviz_config.containers'\
                '._syntax_highlighter.get_path'


def test_syntax_highlighter(dash_duo):

    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True
    cache.init_app(app.server)
    code_file = Path('./tests/data/basic_example.yaml')
    with mock.patch(get_path) as mock_path:
        mock_path.return_value = code_file
        page = _syntax_highlighter.SyntaxHighlighter(app, code_file)
        app.layout = page.layout
        dash_duo.start_server(app)
        assert dash_duo.get_logs() == [], "browser console should contain no error"

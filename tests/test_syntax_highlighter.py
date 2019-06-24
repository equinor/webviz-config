import dash
from webviz_config.common_cache import cache
from webviz_config.containers import _syntax_highlighter


def test_syntax_highlighter(dash_duo):

    app = dash.Dash(__name__)
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.config.suppress_callback_exceptions = True
    cache.init_app(app.server)
    code_file = './tests/data/basic_example.yaml'
    page = _syntax_highlighter.SyntaxHighlighter(app, code_file)
    app.layout = page.layout
    dash_duo.start_server(app)
    assert dash_br.get_logs() == [], "browser console should contain no error"

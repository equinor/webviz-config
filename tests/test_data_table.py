from unittest import mock

import pandas as pd
import dash

from webviz_config.common_cache import CACHE
from webviz_config.generic_plugins import _data_table

# mocked functions
GET_DATA = "webviz_config.generic_plugins._data_table.get_data"


def test_data_table(dash_duo):

    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True
    CACHE.init_app(app.server)
    code_file = "./tests/data/example_data.csv"
    with mock.patch(GET_DATA) as mock_path:
        mock_path.return_value = pd.read_csv(code_file)
        page = _data_table.DataTable(code_file)
        app.layout = page.layout
        dash_duo.start_server(app)
        assert dash_duo.get_logs() == [], "browser console should contain no error"


def test_data_table_with_settings(dash_duo):

    app = dash.Dash(__name__)
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.config.suppress_callback_exceptions = True
    CACHE.init_app(app.server)
    code_file = "./tests/data/example_data.csv"
    with mock.patch(GET_DATA) as mock_path:
        mock_path.return_value = pd.read_csv(code_file)
        page = _data_table.DataTable(
            csv_file=code_file, sorting=False, filtering=False, pagination=False
        )
        app.layout = page.layout
        dash_duo.start_server(app)
        assert dash_duo.get_logs() == [], "browser console should contain no error"

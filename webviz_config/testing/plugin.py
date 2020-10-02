import pytest

import dash
from dash_html_components import Div

from ._monitor_builtin_open import monitor_builtin_open
from ..common_cache import CACHE
from ..themes import default_theme


class WebvizSinglePlugin:
    def __init__(self):
        self._app = dash.Dash(__name__)
        self._configure_app()

    def _configure_app(self):
        self._app.config.suppress_callback_exceptions = True
        CACHE.init_app(self._app.server)
        self._app.webviz_settings = {"theme": default_theme}

    def check_portability(self):
        monitor_builtin_open.start_monitoring()

    @property
    def app(self):
        return self._app


@pytest.fixture
def webviz_single_plugin():
    return WebvizSinglePlugin()

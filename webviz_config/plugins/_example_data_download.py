import dash_html_components as html
from dash import Dash

from .. import WebvizPluginABC


class ExampleDataDownload(WebvizPluginABC):
    def __init__(self, app: Dash, title: str):
        super().__init__()

        self.title = title
        self.set_callbacks(app)

    @property
    def layout(self) -> html.H1:
        return html.H1(self.title)

    def set_callbacks(self, app: Dash) -> None:
        @app.callback(self.plugin_data_output, [self.plugin_data_requested])
        def _user_download_data(data_requested: bool) -> str:
            return (
                WebvizPluginABC.plugin_data_compress(
                    [{"filename": "some_file.txt", "content": "Some download data"}]
                )
                if data_requested
                else ""
            )

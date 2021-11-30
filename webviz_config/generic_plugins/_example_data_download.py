from typing import Optional

from dash import html, Dash

from .. import WebvizPluginABC, EncodedFile


class ExampleDataDownload(WebvizPluginABC):
    def __init__(self, app: Dash, title: str):
        super().__init__()

        self.title = title
        self.set_callbacks(app)

    @property
    def layout(self) -> html.H1:
        return html.H1(self.title)

    def set_callbacks(self, app: Dash) -> None:
        @app.callback(self.plugin_data_output, self.plugin_data_requested)
        def _user_download_data(data_requested: bool) -> Optional[EncodedFile]:
            return (
                WebvizPluginABC.plugin_compressed_data(
                    filename="webviz-data.zip",
                    content=[
                        {"filename": "some_file.txt", "content": "Some download data"}
                    ],
                )
                if data_requested
                else None
            )

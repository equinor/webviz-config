import dash_html_components as html

from .. import WebvizPluginABC


class ExampleDataDownload(WebvizPluginABC):
    def __init__(self, app, title: str):
        super().__init__()

        self.title = title
        self.set_callbacks(app)

    @property
    def layout(self):
        return html.H1(self.title)

    def set_callbacks(self, app):
        @app.callback(self.container_data_output, [self.container_data_requested])
        def _user_download_data(data_requested):
            return (
                WebvizPluginABC.container_data_compress(
                    [{"filename": "some_file.txt", "content": "Some download data"}]
                )
                if data_requested
                else ""
            )

import dash_html_components as html
from dash.dependencies import Input, Output

from .. import WebvizPluginABC


class ExamplePlugin(WebvizPluginABC):
    def __init__(self, app, title: str):
        super().__init__()

        self.title = title

        self.set_callbacks(app)

    @property
    def layout(self):
        return html.Div(
            [
                html.H1(self.title),
                html.Button(
                    id=self.uuid("submit-button"), n_clicks=0, children="Submit"
                ),
                html.Div(id=self.uuid("output-state")),
            ]
        )

    def set_callbacks(self, app):
        @app.callback(
            Output(self.uuid("output-state"), "children"),
            [Input(self.uuid("submit-button"), "n_clicks")],
        )
        def _update_output(n_clicks):
            return f"Button has been pressed {n_clicks} times."

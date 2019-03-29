from uuid import uuid4
import dash_html_components as html
from dash.dependencies import Input, Output


class ExampleContainer:

    def __init__(self, app, title: str):
        self.title = title

        self.button_id = 'submit-button-{}'.format(uuid4())
        self.div_id = 'output-state-{}'.format(uuid4())

        self.set_callbacks(app)

    @property
    def layout(self):
        return html.Div([
                         html.H1(self.title),
                         html.Button(id=self.button_id, n_clicks=0,
                                     children='Submit'),
                         html.Div(id=self.div_id)
                        ])

    def set_callbacks(self, app):
        @app.callback(Output(self.div_id, 'children'),
                      [Input(self.button_id, 'n_clicks')])
        def update_output(n_clicks):
            return 'Button has been pressed {} times.'.format(n_clicks)

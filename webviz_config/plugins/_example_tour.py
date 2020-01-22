import dash_html_components as html

from .. import WebvizPluginABC


class ExampleTour(WebvizPluginABC):
    @property
    def tour_steps(self):
        return [
            {"id": self.uuid("blue_text"), "content": "This is the first step"},
            {"id": self.uuid("red_text"), "content": "This is the second step"},
        ]

    @property
    def layout(self):
        return html.Div(
            children=[
                html.Span(
                    "Here is some blue text to explain... ",
                    id=self.uuid("blue_text"),
                    style={"color": "blue"},
                ),
                html.Span(
                    " ...and here is some red text that also needs an explanation.",
                    id=self.uuid("red_text"),
                    style={"color": "red"},
                ),
            ]
        )

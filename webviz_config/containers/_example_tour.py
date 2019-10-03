from uuid import uuid4

import dash_html_components as html

from .. import WebvizContainerABC


class ExampleTour(WebvizContainerABC):
    def __init__(self):
        self.blue_text_id = f"element-{uuid4()}"
        self.red_text_id = f"element-{uuid4()}"

    @property
    def tour_steps(self):
        return [
            {"id": self.blue_text_id, "content": "This is the first step"},
            {"id": self.red_text_id, "content": "This is the second step"},
        ]

    @property
    def layout(self):
        return html.Div(
            children=[
                html.Span(
                    "Here is some blue text to explain... ",
                    id=self.blue_text_id,
                    style={"color": "blue"},
                ),
                html.Span(
                    " ...and here is some red text that also needs an explanation.",
                    id=self.red_text_id,
                    style={"color": "red"},
                ),
            ]
        )

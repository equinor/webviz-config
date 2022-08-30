from typing import Type, Union

from dash.development.base_component import Component
from dash import html

from webviz_config.webviz_plugin_subclasses import ViewElementABC


class TextViewElement(ViewElementABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        TEXT = "text"

    def __init__(self) -> None:
        super().__init__()

    def inner_layout(self) -> Union[str, Type[Component]]:
        return html.Div(
            id=self.register_component_unique_id(TextViewElement.Ids.TEXT),
            children=[
                html.H1("Hello"),
                """
                This is an example plugin.
                Please have a look how views and settings are working in this new environment =).
                """,
            ],
        )

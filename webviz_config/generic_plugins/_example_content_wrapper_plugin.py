from typing import List, Optional, Type, Union, overload

from dash.development.base_component import Component
from dash import html, Dash, Input, Output

from .. import WebvizPluginABC

from ..webviz_plugin_subclasses import ViewABC, ViewElementABC, SettingsGroupABC


class ExampleViewElement(ViewElementABC):
    def __init__(self) -> None:
        super().__init__()

    def layout(self) -> Union[str, Type[Component]]:
        return html.Div(
            [
                html.H1("Title"),
                html.Button(
                    id=self.uuid("submit-button"), n_clicks=0, children="Submit"
                ),
                html.Div(id=self.uuid("output-state")),
            ]
        )


class ExampleSettingsGroup(SettingsGroupABC):
    def __init__(self, title: str) -> None:
        super().__init__(title)

    def layout(self) -> Component:
        return html.Div(html.Select(self.title))


class ExampleView(ViewABC):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._view_element = ExampleViewElement()
        self._setting = ExampleSettingsGroup("Example Settings")

    def view_elements(self) -> List[ViewElementABC]:
        return [self._view_element]

    def settings(self) -> List[SettingsGroupABC]:
        return [self._setting]


class ExampleContentWrapperPlugin(WebvizPluginABC):
    def __init__(self, app: Dash, title: str):
        super().__init__(app)

        self.title = title

        self._first_view = ExampleView("First View")
        # self.set_callbacks(app)

    def views(self) -> List[ViewABC]:
        return [self._first_view]

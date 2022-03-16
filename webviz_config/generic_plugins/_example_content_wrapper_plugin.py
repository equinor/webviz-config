from typing import List, Optional, Tuple, Type, Union, overload

from dash.development.base_component import Component
from dash import html, Dash, Input, Output, dash_table

import webviz_core_components as wcc

from .. import WebvizPluginABC

from ..webviz_plugin_subclasses import ViewABC, ViewElementABC, SettingsGroupABC


class TextViewElement(ViewElementABC):
    def __init__(self) -> None:
        super().__init__()

    def layout(self) -> Union[str, Type[Component]]:
        return html.Div(
            id="text",
            children=[
                html.H1("Hello"),
                "This is an example plugin. Please have a look how views and settings are working in this new environment =).",
            ],
        )


class PlotViewElement(ViewElementABC):
    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__()
        self.data = data

    def layout(self) -> Union[str, Type[Component]]:
        return html.Div(
            children=[
                wcc.Graph(
                    id="my-graph",
                    figure={
                        "data": [
                            {
                                "x": [x[1] for x in self.data],
                                "y": [x[0] for x in self.data],
                            }
                        ],
                        "layout": {
                            "title": "Example Graph Swapped",
                        },
                    },
                    config={
                        "responsive": True,
                    },
                )
            ],
        )


class TableViewElement(ViewElementABC):
    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__()
        self.data = data

    def layout(self) -> Union[str, Type[Component]]:
        return dash_table.DataTable(
            id="my-table",
            columns=[{"id": "x", "name": "X"}, {"id": "y", "name": "Y"}],
            data=[{"x": d[0], "y": d[1]} for d in self.data],
        )


class PlotViewSettingsGroup(SettingsGroupABC):
    def __init__(self) -> None:
        super().__init__("Plot coordinate system")

    def layout(self) -> Component:
        return wcc.RadioItems(
            id="coordinates-selector",
            options=[
                {
                    "label": "x - y",
                    "value": "xy",
                },
                {
                    "label": "y - x",
                    "value": "yx",
                },
            ],
            value="xy",
        )


class TableViewSettingsGroup(SettingsGroupABC):
    def __init__(self) -> None:
        super().__init__("Table orientation")

    def layout(self) -> Component:
        return wcc.RadioItems(
            id="order-selector",
            options=[
                {
                    "label": "ASC",
                    "value": "asc",
                },
                {
                    "label": "DESC",
                    "value": "desc",
                },
            ],
            value="asc",
        )


class SharedSettingsGroup(SettingsGroupABC):
    def __init__(self) -> None:
        super().__init__("Kindness")

    def layout(self) -> Component:
        return wcc.RadioItems(
            id="kindness-selector",
            options=[
                {
                    "label": "friendly",
                    "value": "friendly",
                },
                {
                    "label": "unfriendly",
                    "value": "unfriendly",
                },
            ],
            value="friendly",
        )


class PlotView(ViewABC):
    def __init__(self, app: Dash, data: List[Tuple[int, int]]) -> None:
        super().__init__("Plot")
        self.data = data

        self.my_elements = [TextViewElement(), PlotViewElement(self.data)]
        self.my_settings: List[SettingsGroupABC] = [PlotViewSettingsGroup()]

        self._set_callbacks(app)

    def view_elements(self) -> List[ViewElementABC]:
        return self.my_elements

    def settings(self) -> List[SettingsGroupABC]:
        return self.my_settings

    def _set_callbacks(self, app: Dash) -> None:
        @app.callback(
            Output("my-graph", "figure"),
            Input("coordinates-selector", "value"),
        )
        def swap_coordinates(coordinates: str) -> dict:
            if coordinates == "yx":
                return {
                    "data": [
                        {
                            "x": [x[1] for x in self.data],
                            "y": [x[0] for x in self.data],
                        }
                    ],
                    "layout": {"title": "Example Graph Swapped"},
                }
            return {
                "data": [
                    {
                        "x": [x[0] for x in self.data],
                        "y": [x[1] for x in self.data],
                    }
                ],
                "layout": {"title": "Example Graph"},
            }


class TableView(ViewABC):
    def __init__(self, app: Dash, data: List[Tuple[int, int]]) -> None:
        super().__init__("Table")
        self.data = data

        self.my_elements = [TextViewElement(), TableViewElement(self.data)]
        self.my_settings: List[SettingsGroupABC] = [TableViewSettingsGroup()]

        self._set_callbacks(app)

    def view_elements(self) -> List[ViewElementABC]:
        return self.my_elements

    def settings(self) -> List[SettingsGroupABC]:
        return self.my_settings

    def _set_callbacks(self, app: Dash) -> None:
        @app.callback(
            Output("my-table", "data"),
            Input("order-selector", "value"),
        )
        def swap_order(order: str) -> List[dict]:
            data = self.data.copy()
            if order == "desc":
                data.reverse()
            return [{"x": d[0], "y": d[1]} for d in data]


class ExampleContentWrapperPlugin(WebvizPluginABC):
    def __init__(self, app: Dash, title: str):
        super().__init__(app)

        self.data = [(x, x * x) for x in range(0, 10)]
        self.app = app
        self.title = title

        self.my_views = [PlotView(app, self.data), TableView(app, self.data)]
        self.my_shared_settings: List[SettingsGroupABC] = [SharedSettingsGroup()]

        self._set_callbacks(app)

    def views(self) -> List[ViewABC]:
        return self.my_views

    def shared_settings(self) -> Optional[List[SettingsGroupABC]]:
        return self.my_shared_settings

    def _set_callbacks(self, app: Dash) -> None:
        @app.callback(
            Output("text", "children"),
            Input("kindness-selector", "value"),
        )
        def change_kindness(kindness: str) -> Component:
            if kindness == "friendly":
                return [
                    html.H1("Hello"),
                    "I am an example plugin. Please have a look how views and settings are working in this my environment =).",
                ]
            return [
                html.H1("Goodbye"),
                "I am a bloody example plugin. Leave me alone! =(",
            ]

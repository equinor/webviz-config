from typing import Any, Dict, List, Optional, Tuple, Type, Union

from dash.development.base_component import Component
from dash import (
    html,
    Dash,
    Input,
    Output,
    State,
    dash_table,
    callback_context,
    no_update,
)
from dash.exceptions import PreventUpdate

import pandas as pd

import webviz_core_components as wcc

from .. import WebvizPluginABC, EncodedFile

from ..deprecation_decorators import deprecated_plugin
from ..webviz_plugin_subclasses import ViewABC, ViewElementABC, SettingsGroupABC


class TextViewElement(ViewElementABC):
    def __init__(self) -> None:
        super().__init__()

    def layout(self) -> Union[str, Type[Component]]:
        return html.Div(
            id=self.register_component_uuid("text"),
            children=[
                html.H1("Hello"),
                "This is an example plugin. Please have a look how views and settings are working in this new environment =).",
            ],
        )


class PlotViewElementSettings(SettingsGroupABC):
    def __init__(self) -> None:
        super().__init__("Plot coordinate system")

    def layout(self) -> Component:
        return wcc.Select(
            id=self.register_component_uuid("test"),
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
            persistence=True,
        )


class PlotViewElement(ViewElementABC):
    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__(flex_grow=8, loading_mask=ViewElementABC.LoadingMask.Graph)
        self.data = data

        self.add_settings_group(PlotViewSettingsGroup(), "PlotViewSettings")

    def layout(self) -> Union[str, Type[Component]]:
        return html.Div(
            style={"height": "20vh"},
            children=[
                wcc.Graph(
                    id=self.register_component_uuid("my-graph"),
                    figure={
                        "data": [
                            {
                                "x": [x[0] for x in self.data],
                                "y": [x[1] for x in self.data],
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

    @staticmethod
    def download_data_df(graph_figure: Dict[str, Any]) -> pd.DataFrame:
        graph_data: Optional[List[Dict[str, Any]]] = graph_figure.get("data", None)
        if not graph_data:
            return "No data present in graph figure"

        x = graph_data[0].get("x", None)
        y = graph_data[0].get("y", None)
        if x is None or y is None:
            return f"Missing x or y data: x = {x} and y = {y}"

        df = pd.DataFrame(
            columns=["x", "y"],
        )
        df["x"] = x
        df["y"] = y
        return df

    def _set_callbacks(self, app: Dash) -> None:
        @app.callback(
            self.view_element_data_output,
            self.view_element_data_requested,
            State(self.component_uuid("my-graph").to_string(), "figure"),
            prevent_initial_call=True,
        )
        def _download_data(
            data_requested: Union[int, None], graph_figure: Dict[str, Any]
        ) -> Union[EncodedFile, str]:
            if data_requested is None:
                raise PreventUpdate

            return WebvizPluginABC.plugin_data_compress(
                [
                    {
                        "filename": f"{self.component_uuid('my-graph').to_string()}.csv",
                        "content": self.download_data_df(graph_figure).to_csv(
                            index=False
                        ),
                    }
                ]
            )


class TableViewElement(ViewElementABC):
    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__(loading_mask=ViewElementABC.LoadingMask.Table)
        self.data = data

    def layout(self) -> Union[str, Type[Component]]:
        return dash_table.DataTable(
            id=self.register_component_uuid("my-table"),
            columns=[{"id": "x", "name": "X"}, {"id": "y", "name": "Y"}],
            data=[{"x": d[0], "y": d[1]} for d in self.data],
        )

    @staticmethod
    def download_data_df(table_data: List[Dict[str, int]]) -> pd.DataFrame:
        x = []
        y = []
        for index, elm in enumerate(table_data):
            _x = elm.get("x", None)
            _y = elm.get("y", None)
            if _x is None:
                raise ValueError(f'No "x" column data in table at index {index}')
            if _y is None:
                raise ValueError(f'No "y" column data in table at index {index}')
            x.append(_x)
            y.append(_y)

        df = pd.DataFrame(
            columns=["x", "y"],
        )
        df["x"] = x
        df["y"] = y

    def _set_callbacks(self, app: Dash) -> None:
        @app.callback(
            self.view_element_data_output,
            self.view_element_data_requested,
            State(self.component_uuid("my-table").to_string(), "data"),
            prevent_initial_call=True,
        )
        def _download_data(
            data_requested: Union[int, None], table_data: List[Dict[str, int]]
        ) -> Union[EncodedFile, str]:
            if data_requested is None:
                raise PreventUpdate

            if not table_data:
                return "No data present in table"

            return WebvizPluginABC.plugin_data_compress(
                [
                    {
                        "filename": f"{self.component_uuid('my-table').to_string()}.csv",
                        "content": self.download_data_df(table_data).to_csv(
                            index=False
                        ),
                    }
                ]
            )


class PlotViewSettingsGroup(SettingsGroupABC):
    def __init__(self) -> None:
        super().__init__("Plot coordinate system")

    def layout(self) -> Component:
        return wcc.Dropdown(
            id=self.register_component_uuid("coordinates-selector"),
            label="Coordinates",
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
            id=self.register_component_uuid("order-selector"),
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
        super().__init__("Shared settings")

    def layout(self) -> Component:
        return html.Div(
            children=[
                wcc.Label("Kindness"),
                wcc.RadioItems(
                    id=self.register_component_uuid("kindness-selector"),
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
                ),
                wcc.Label("Power"),
                wcc.RadioItems(
                    id=self.register_component_uuid("power-selector"),
                    options=[
                        {
                            "label": "2",
                            "value": "2",
                        },
                        {
                            "label": "3",
                            "value": "3",
                        },
                    ],
                    value="2",
                ),
            ]
        )


class PlotView(ViewABC):
    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__("Plot")
        self.data = data

        row = self.add_row()
        row.add_view_element(TextViewElement(), "Text")
        row.add_view_element(PlotViewElement(self.data), "Plot")

        self.add_settings_group(PlotViewSettingsGroup(), "PlotSettings")


class TableView(ViewABC):
    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__("Table")
        self.data = data

        self.table_view = TableViewElement(self.data)

        self.add_view_element(TextViewElement(), "Text")
        self.add_view_element(self.table_view, "Table")

        self.add_settings_group(TableViewSettingsGroup(), settings_group_id="Settings")

    def _set_callbacks(self, app: Dash) -> None:
        @app.callback(
            Output(self.table_view.component_uuid("my-table").to_string(), "data"),
            Input(self.settings_group_uuid("Settings", "order-selector"), "value"),
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

        self.add_view(PlotView(self.data), "PlotView")
        self.add_view(TableView(self.data), "TableView")

        self.settings_group = SharedSettingsGroup()
        self.add_shared_settings_group(
            self.settings_group,
            "SharedSettings",
            visible_in_views=[self.view("PlotView").uuid()],
        )

        self._set_callbacks(app)

    @property
    def tour_steps(self) -> List[dict]:
        return [
            {
                "id": self.view("PlotView")
                .view_element("Plot")
                .component_uuid("my-graph"),
                "content": "This is a plot showing data.",
            },
            {
                "id": self.view("PlotView")
                .view_element("Plot")
                .component_uuid("my-graph"),
                "content": "Plot showing plot data.",
            },
            {
                "id": self.view("TableView")
                .view_element("Table")
                .component_uuid("my-table"),
                "content": "A table showing data.",
            },
        ]

    def _set_callbacks(self, app: Dash) -> None:
        @app.callback(
            self.plugin_data_output,
            self.plugin_data_requested,
            State(
                self.view("PlotView")
                .view_element("Plot")
                .component_uuid("my-graph")
                .to_string(),
                "figure",
            ),
            # State(
            #     self.view("TableView")
            #     .view_element("Table")
            #     .component_uuid("my-table")
            #     .to_string(),
            #     "data",
            # ),
        )
        def _download_plugin_data(
            data_requested: Union[int, None],
            graph_figure: Dict[str, Any],
            # table_data: List[Dict[str, int]],
        ) -> Union[EncodedFile, str]:
            if data_requested is None:
                raise PreventUpdate

            plot_data_csv = PlotViewElement.download_data_df(graph_figure).to_csv(
                index=False
            )
            # table_data_csv = TableViewElement.download_data_df(table_data).to_csv(
            #     index=False
            # )

            return WebvizPluginABC.plugin_data_compress(
                [
                    {
                        "filename": f"{self.view('PlotView').view_element('Plot').component_uuid('my-graph').to_string()}.csv",
                        "content": plot_data_csv,
                    },
                    # {
                    #     "filename": f"{self.view('TableView').view_element('Table').component_uuid('my-table').to_string()}.csv",
                    #     "content": table_data_csv,
                    # },
                ]
            )

        @app.callback(
            Output(
                self.view("PlotView")
                .view_element("Text")
                .component_uuid("text")
                .to_string(),
                "children",
            ),
            Input(
                self.settings_group.component_uuid("kindness-selector").to_string(),
                "value",
            ),
        )
        def pseudo1(kindness: str) -> Component:
            return change_kindness(kindness)

        @app.callback(
            Output(
                self.view("TableView")
                .view_element("Text")
                .component_uuid("text")
                .to_string(),
                "children",
            ),
            Input(
                self.settings_group.component_uuid("kindness-selector").to_string(),
                "value",
            ),
        )
        def pseudo2(kindness: str) -> Component:
            return change_kindness(kindness)

        def change_kindness(kindness: str) -> Component:
            if kindness == "friendly":
                return [
                    html.H1("Hello"),
                    "I am an example plugin. Please have a look how views and settings are working in my environment =).",
                ]

            return [
                html.H1("Goodbye"),
                "I am a bloody example plugin. Leave me alone! =(",
            ]

        @app.callback(
            Output(
                self.view("PlotView")
                .view_elements()[1]
                .component_uuid("my-graph")
                .to_string(),
                "figure",
            ),
            [
                Input(
                    self.settings_group.component_uuid("power-selector").to_string(),
                    "value",
                ),
                Input(
                    self.view("PlotView")
                    .settings_group("PlotSettings")
                    .component_uuid("coordinates-selector")
                    .to_string(),
                    "value",
                ),
            ],
        )
        def change_power_and_coordinates(power: str, coordinates: str) -> Component:
            if power == "2":
                self.data = [(x, x * x) for x in range(0, 10)]
            else:
                self.data = [(x, x * x * x) for x in range(0, 10)]

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


@deprecated_plugin("This is an example plugin that should be removed.")
class ExampleContentWrapperPlugin2(WebvizPluginABC):
    def __init__(self, app: Dash, title: str):
        super().__init__(app)

        self.data = [(x, x * x) for x in range(0, 10)]
        self.app = app
        self.title = title

        self.add_view(PlotView(self.data), "PlotView")

from typing import Any, Dict, List, Optional, Tuple, Type, Union

from dash.development.base_component import Component
from dash import html, Input, Output, State, dash_table, callback
from dash.exceptions import PreventUpdate

import pandas as pd

import webviz_core_components as wcc

from .. import WebvizPluginABC, EncodedFile

from ..deprecation_decorators import deprecated_plugin
from ..webviz_plugin_subclasses import ViewABC, ViewElementABC, SettingsGroupABC


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


class PlotViewElementSettings(SettingsGroupABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        COORDINATES = "coordinates"

    def __init__(self) -> None:
        super().__init__("Plot coordinate system")

    def layout(self) -> List[Component]:
        return [
            wcc.Select(
                id=self.register_component_unique_id(
                    PlotViewElementSettings.Ids.COORDINATES
                ),
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
        ]


class PlotViewElement(ViewElementABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        GRAPH = "graph"

    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__(flex_grow=8)
        self.data = data

        self.add_settings_group(PlotViewSettingsGroup(), "PlotViewSettings")

    def inner_layout(self) -> Union[str, Type[Component]]:
        return html.Div(
            style={"height": "20vh"},
            children=[
                wcc.Graph(
                    id=self.register_component_unique_id(PlotViewElement.Ids.GRAPH),
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

        x_values = graph_data[0].get("x", None)
        y_values = graph_data[0].get("y", None)
        if x_values is None or y_values is None:
            return f"Missing x or y data: x = {x_values} and y = {y_values}"

        df = pd.DataFrame(
            columns=["x", "y"],
        )
        df["x"] = x_values
        df["y"] = y_values
        return df

    def set_callbacks(self) -> None:
        @callback(
            self.view_element_data_output(),
            self.view_element_data_requested(),
            State(
                self.component_unique_id(PlotViewElement.Ids.GRAPH).to_string(),
                "figure",
            ),
        )
        def _download_data(
            data_requested: Union[int, None], graph_figure: Dict[str, Any]
        ) -> Union[EncodedFile, str]:
            if data_requested is None:
                raise PreventUpdate

            return WebvizPluginABC.plugin_data_compress(
                [
                    {
                        "filename": f"{self.component_unique_id('my-graph').to_string()}.csv",
                        "content": self.download_data_df(graph_figure).to_csv(
                            index=False
                        ),
                    }
                ]
            )


class TableViewElement(ViewElementABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        TABLE = "table"

    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__()
        self.data = data

    def inner_layout(self) -> Union[str, Type[Component]]:
        return dash_table.DataTable(
            id=self.register_component_unique_id(TableViewElement.Ids.TABLE),
            columns=[{"id": "x", "name": "X"}, {"id": "y", "name": "Y"}],
            data=[{"x": d[0], "y": d[1]} for d in self.data],
        )

    @staticmethod
    def download_data_df(table_data: List[Dict[str, int]]) -> pd.DataFrame:
        x_values = []
        y_values = []
        for index, elm in enumerate(table_data):
            _x = elm.get("x", None)
            _y = elm.get("y", None)
            if _x is None:
                raise ValueError(f'No "x" column data in table at index {index}')
            if _y is None:
                raise ValueError(f'No "y" column data in table at index {index}')
            x_values.append(_x)
            y_values.append(_y)

        df = pd.DataFrame(
            columns=["x", "y"],
        )
        df["x"] = x_values
        df["y"] = y_values
        return df

    def set_callbacks(self) -> None:
        @callback(
            self.view_element_data_output(),
            self.view_element_data_requested(),
            State(self.component_unique_id("my-table").to_string(), "data"),
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
                        "filename": f"{self.component_unique_id('my-table').to_string()}.csv",
                        "content": self.download_data_df(table_data).to_csv(
                            index=False
                        ),
                    }
                ]
            )


class PlotViewSettingsGroup(SettingsGroupABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        COORDINATES_SELECTOR = "coordinates-selector"

    def __init__(self) -> None:
        super().__init__("Plot coordinate system")

    def layout(self) -> List[Component]:
        return [
            wcc.Dropdown(
                id=self.register_component_unique_id(
                    PlotViewSettingsGroup.Ids.COORDINATES_SELECTOR
                ),
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
        ]


class TableViewSettingsGroup(SettingsGroupABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        ORDER_SELECTOR = "order-selector"

    def __init__(self) -> None:
        super().__init__("Table orientation")

    def layout(self) -> List[Component]:
        return [
            wcc.RadioItems(
                id=self.register_component_unique_id(
                    TableViewSettingsGroup.Ids.ORDER_SELECTOR
                ),
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
        ]


class SharedSettingsGroup(SettingsGroupABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        KINDNESS_SELECTOR = "kindness-selector"
        POWER_SELECTOR = "power-selector"

    def __init__(self) -> None:
        super().__init__("Shared settings")

    def layout(self) -> List[Component]:
        return [
            html.Div(
                children=[
                    wcc.Label("Kindness"),
                    wcc.RadioItems(
                        id=self.register_component_unique_id(
                            SharedSettingsGroup.Ids.KINDNESS_SELECTOR
                        ),
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
                        id=self.register_component_unique_id(
                            SharedSettingsGroup.Ids.POWER_SELECTOR
                        ),
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
        ]


class PlotView(ViewABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        TEXT = TextViewElement.Ids.TEXT
        PLOT = "plot"
        PLOT_SETTINGS = "plot-settings"

    def __init__(self, data: List[Tuple[int, int]]) -> None:
        super().__init__("Plot")
        self.data = data

        self._plot_view = PlotViewElement(self.data)

        row = self.add_row()
        row.add_view_element(TextViewElement(), PlotView.Ids.TEXT)
        row.add_view_element(self._plot_view, PlotView.Ids.PLOT)

        self.add_settings_group(PlotViewSettingsGroup(), PlotView.Ids.PLOT_SETTINGS)

    def set_callbacks(self) -> None:
        @callback(
            self.view_data_output(),
            self.view_data_requested(),
            State(
                self._plot_view.component_unique_id(
                    PlotViewElement.Ids.GRAPH
                ).to_string(),
                "figure",
            ),
        )
        def _download_data(
            data_requested: Union[int, None],
            graph_figure: Dict[str, Any],
        ) -> Union[EncodedFile, str]:
            if data_requested is None:
                raise PreventUpdate

            return WebvizPluginABC.plugin_data_compress(
                [
                    {
                        "filename": f"""{
                            self._plot_view.component_unique_id(
                                PlotViewElement.Ids.GRAPH
                            ).to_string()}.csv""",
                        "content": PlotViewElement.download_data_df(
                            graph_figure
                        ).to_csv(index=False),
                    },
                ]
            )


class TableView(ViewABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        TEXT = TextViewElement.Ids.TEXT
        TABLE = "table"
        TABLE_SETTINGS = "table-settings"

    def __init__(
        self,
        data: List[Tuple[int, int]],
    ) -> None:
        super().__init__("Table")
        self.data = data

        self.table_view = TableViewElement(self.data)

        self.add_view_element(TextViewElement(), TableView.Ids.TEXT)
        self.add_view_element(self.table_view, TableView.Ids.TABLE)

        self.add_settings_group(
            TableViewSettingsGroup(), settings_group_id=TableView.Ids.TABLE_SETTINGS
        )

    def set_callbacks(self) -> None:
        @callback(
            Output(
                self.table_view.component_unique_id(
                    TableViewElement.Ids.TABLE
                ).to_string(),
                "data",
            ),
            Input(
                self.settings_group_unique_id(
                    TableView.Ids.TABLE_SETTINGS,
                    TableViewSettingsGroup.Ids.ORDER_SELECTOR,
                ),
                "value",
            ),
        )
        def swap_order(order: str) -> List[dict]:
            data = self.data.copy()
            if order == "desc":
                data.reverse()
            return [{"x": d[0], "y": d[1]} for d in data]

        @callback(
            self.view_data_output(),
            self.view_data_requested(),
            State(
                self.table_view.component_unique_id(
                    TableViewElement.Ids.TABLE
                ).to_string(),
                "data",
            ),
        )
        def _download_data(
            data_requested: Union[int, None],
            table_data: List[Dict[str, int]],
        ) -> Union[EncodedFile, str]:
            if data_requested is None:
                raise PreventUpdate

            return WebvizPluginABC.plugin_data_compress(
                [
                    {
                        "filename": f"""{
                            self.table_view.component_unique_id(
                                TableViewElement.Ids.TABLE).to_string()
                            }.csv""",
                        "content": TableViewElement.download_data_df(table_data).to_csv(
                            index=False
                        ),
                    },
                ]
            )


class ExampleWlfPlugin(WebvizPluginABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        PLOT_VIEW = "plot-view"
        TABLE_VIEW = "table-view"
        SHARED_SETTINGS = "shared-settings"

    def __init__(self, title: str):
        super().__init__()

        self.data = [(x, x * x) for x in range(0, 10)]
        self.title = title

        self.add_view(PlotView(self.data), ExampleWlfPlugin.Ids.PLOT_VIEW)
        self.add_view(TableView(self.data), ExampleWlfPlugin.Ids.TABLE_VIEW)

        self.settings_group = SharedSettingsGroup()
        self.add_shared_settings_group(
            self.settings_group, ExampleWlfPlugin.Ids.SHARED_SETTINGS
        )

    @property
    def tour_steps(self) -> List[dict]:
        return [
            {
                "id": self.view(ExampleWlfPlugin.Ids.PLOT_VIEW)
                .view_element(PlotView.Ids.TEXT)
                .component_unique_id(TextViewElement.Ids.TEXT),
                "content": "Greetings from your example plugin.",
            },
            {
                "id": self.settings_group.component_unique_id("kindness-selector"),
                "content": "You can change here if this shall be friendly or not.",
            },
            {
                "id": self.view(ExampleWlfPlugin.Ids.PLOT_VIEW)
                .view_element(PlotView.Ids.PLOT)
                .component_unique_id(PlotViewElement.Ids.GRAPH),
                "content": "Over here you see a plot that shows x² or x³.",
            },
            {
                "id": self.settings_group.component_unique_id(
                    ExampleWlfPlugin.Ids.SHARED_SETTINGS
                ),
                "content": "You can change here which exponent you prefer.",
            },
            {
                "id": self.view(ExampleWlfPlugin.Ids.PLOT_VIEW)
                .settings_group(PlotView.Ids.PLOT_SETTINGS)
                .component_unique_id(PlotViewSettingsGroup.Ids.COORDINATES_SELECTOR),
                "content": "...and here you can swap the axes.",
            },
            {
                "id": self.view(ExampleWlfPlugin.Ids.TABLE_VIEW)
                .view_element(TableView.Ids.TABLE)
                .component_unique_id(TableViewElement.Ids.TABLE),
                "content": "There is also a table visualizing the data.",
            },
            {
                "id": self.view(ExampleWlfPlugin.Ids.TABLE_VIEW)
                .settings_group(TableView.Ids.TABLE_SETTINGS)
                .component_unique_id(TableViewSettingsGroup.Ids.ORDER_SELECTOR),
                "content": "You can change the order of the table here.",
            },
        ]

    def set_callbacks(self) -> None:
        @callback(
            Output(
                self.view(ExampleWlfPlugin.Ids.PLOT_VIEW)
                .view_element(PlotView.Ids.TEXT)
                .component_unique_id(TextViewElement.Ids.TEXT)
                .to_string(),
                "children",
            ),
            Input(
                self.settings_group.component_unique_id(
                    SharedSettingsGroup.Ids.KINDNESS_SELECTOR
                ).to_string(),
                "value",
            ),
        )
        def pseudo1(kindness: str) -> Component:
            return change_kindness(kindness)

        @callback(
            Output(
                self.view(ExampleWlfPlugin.Ids.TABLE_VIEW)
                .view_element(TableView.Ids.TEXT)
                .component_unique_id(TextViewElement.Ids.TEXT)
                .to_string(),
                "children",
            ),
            Input(
                self.settings_group.component_unique_id(
                    SharedSettingsGroup.Ids.KINDNESS_SELECTOR
                ).to_string(),
                "value",
            ),
        )
        def pseudo2(kindness: str) -> Component:
            return change_kindness(kindness)

        def change_kindness(kindness: str) -> Component:
            if kindness == "friendly":
                return [
                    html.H1("Hello"),
                    """
                    I am an example plugin.
                    Please have a look how views and settings are working in my environment =).
                    """,
                ]

            return [
                html.H1("Goodbye"),
                "I am a bloody example plugin. Leave me alone! =(",
            ]

        @callback(
            Output(
                self.view(ExampleWlfPlugin.Ids.PLOT_VIEW)
                .settings_group(PlotView.Ids.PLOT_SETTINGS)
                .component_unique_id(PlotViewSettingsGroup.Ids.COORDINATES_SELECTOR)
                .to_string(),
                "options",
            ),
            Input(
                self.settings_group.component_unique_id(
                    SharedSettingsGroup.Ids.POWER_SELECTOR
                ).to_string(),
                "value",
            ),
        )
        def change_selection(power: str) -> list:
            if power == "2":
                return [
                    {
                        "label": "x - y",
                        "value": "xy",
                    },
                    {
                        "label": "y - x",
                        "value": "yx",
                    },
                ]

            return [
                {
                    "label": "x - y",
                    "value": "xy",
                },
            ]

        @callback(
            Output(
                self.view(ExampleWlfPlugin.Ids.PLOT_VIEW)
                .view_elements()[1]
                .component_unique_id(PlotViewElement.Ids.GRAPH)
                .to_string(),
                "figure",
            ),
            [
                Input(
                    self.settings_group.component_unique_id(
                        SharedSettingsGroup.Ids.POWER_SELECTOR
                    ).to_string(),
                    "value",
                ),
                Input(
                    self.view(ExampleWlfPlugin.Ids.PLOT_VIEW)
                    .settings_group(PlotView.Ids.PLOT_SETTINGS)
                    .component_unique_id(PlotViewSettingsGroup.Ids.COORDINATES_SELECTOR)
                    .to_string(),
                    "value",
                ),
            ],
        )
        def change_power_and_coordinates(power: str, coordinates: str) -> dict:
            layout = {
                "title": "Example Graph Swapped",
                "margin": {"t": 50, "r": 20, "b": 20, "l": 20},
            }
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
                    "layout": layout,
                }
            return {
                "data": [
                    {
                        "x": [x[0] for x in self.data],
                        "y": [x[1] for x in self.data],
                    }
                ],
                "layout": layout,
            }


@deprecated_plugin("This is an example plugin that should be removed.")
class ExampleWlfPlugin2(WebvizPluginABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        PLOT_VIEW = "plot-view"

    def __init__(self, title: str):
        super().__init__()

        self.data = [(x, x * x) for x in range(0, 10)]
        self.title = title

        self.add_view(PlotView(self.data), ExampleWlfPlugin2.Ids.PLOT_VIEW)

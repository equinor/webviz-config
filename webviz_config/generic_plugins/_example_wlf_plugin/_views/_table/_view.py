from dataclasses import dataclass
from typing import Dict, List, Tuple, Type, Union
import sys

from dash.development.base_component import Component
from dash import html, Input, Output, State, dash_table, callback
from dash.exceptions import PreventUpdate

import pandas as pd

import webviz_core_components as wcc

from webviz_config.utils import callback_typecheck, StrEnum
from webviz_config import WebvizPluginABC, EncodedFile

from webviz_config.webviz_plugin_subclasses import (
    ViewABC,
    ViewElementABC,
    SettingsGroupABC,
)

from webviz_config.generic_plugins._example_wlf_plugin._shared_view_elements import (
    TextViewElement,
)

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated


class Kindness(StrEnum):
    FRIENDLY = "friendly"
    UNFRIENDLY = "unfriendly"


class Order(StrEnum):
    ASC = "asc"
    DESC = "desc"


class TableViewElement(ViewElementABC):
    class Ids(StrEnum):
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

    def compressed_plugin_data(
        self, table_data: List[Dict[str, int]]
    ) -> Union[EncodedFile, str]:
        return WebvizPluginABC.plugin_data_compress(
            [
                {
                    "filename": f"""{
                        self.component_unique_id(TableViewElement.Ids.TABLE).to_string()
                    }.csv""",
                    "content": self.download_data_df(table_data).to_csv(index=False),
                }
            ]
        )

    def set_callbacks(self) -> None:
        @callback(
            self.view_element_data_output(),
            self.view_element_data_requested(),
            State(
                self.component_unique_id(TableViewElement.Ids.TABLE).to_string(), "data"
            ),
        )
        def _download_data(
            data_requested: Union[int, None], table_data: List[Dict[str, int]]
        ) -> Union[EncodedFile, str]:
            if data_requested is None:
                raise PreventUpdate

            if not table_data:
                return "No data present in table"

            return self.compressed_plugin_data(table_data)


class TableViewSettingsGroup(SettingsGroupABC):
    class Ids(StrEnum):
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
                        "value": Order.ASC,
                    },
                    {
                        "label": "DESC",
                        "value": Order.DESC,
                    },
                ],
                value=Order.ASC,
            )
        ]


class TableView(ViewABC):
    class Ids(StrEnum):
        TEXT = "text"
        TABLE = "table"
        TABLE_SETTINGS = "table-settings"

    @dataclass
    class Slots:
        kindness_selector: Annotated[Input, str]
        power_selector: Annotated[Input, str]

    def __init__(self, data: List[Tuple[int, int]], slots: Slots) -> None:
        super().__init__("Table")
        self.data = data

        self.slots = slots

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
            self.slots.power_selector,
            Input(
                self.settings_group_unique_id(
                    TableView.Ids.TABLE_SETTINGS,
                    TableViewSettingsGroup.Ids.ORDER_SELECTOR,
                ),
                "value",
            ),
        )
        @callback_typecheck
        def _swap_order_and_power(power: int, order: Order) -> List[dict]:
            if power == 2:
                self.data = [(x, x * x) for x in range(0, 10)]
            else:
                self.data = [(x, x * x * x) for x in range(0, 10)]
            data = self.data.copy()
            if order == Order.DESC:
                data.reverse()
            return [{"x": d[0], "y": d[1]} for d in data]

        @callback(
            Output(
                self.view_element(TableView.Ids.TEXT)
                .component_unique_id(TextViewElement.Ids.TEXT)
                .to_string(),
                "children",
            ),
            self.slots.kindness_selector,
        )
        @callback_typecheck
        def _change_kindness(kindness: Kindness) -> Component:
            if kindness == Kindness.FRIENDLY:
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

            return self.table_view.compressed_plugin_data(table_data)

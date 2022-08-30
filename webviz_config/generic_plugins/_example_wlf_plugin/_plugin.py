from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from dash.development.base_component import Component
from dash import html, Input, Output, State, dash_table, callback
from dash.exceptions import PreventUpdate

import pandas as pd

import webviz_core_components as wcc

from ... import WebvizPluginABC, EncodedFile

from ...webviz_plugin_subclasses import ViewABC, ViewElementABC, SettingsGroupABC

from ...webviz_plugin_subclasses import callback_typecheck

from .views._plot import PlotView, PlotViewElement, PlotViewSettingsGroup
from .views._table import TableView, TableViewElement, TableViewSettingsGroup
from ._shared_view_elements import TextViewElement


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


class ExampleWlfPlugin(WebvizPluginABC):
    class Ids:
        # pylint: disable=too-few-public-methods
        PLOT_VIEW = "plot-view"
        TABLE_VIEW = "table-view"
        SHARED_SETTINGS = "shared-settings"

    def __init__(self, title: str):
        super().__init__(stretch=True)

        self.data = [(x, x * x) for x in range(0, 10)]
        self.title = title

        self.settings_group = SharedSettingsGroup()
        self.add_shared_settings_group(
            self.settings_group, ExampleWlfPlugin.Ids.SHARED_SETTINGS
        )

        self.add_view(
            PlotView(
                self.data,
                PlotView.Slots(
                    kindness_selector=Input(
                        self.settings_group.component_unique_id(
                            SharedSettingsGroup.Ids.KINDNESS_SELECTOR
                        ).to_string(),
                        "value",
                    ),
                    power_selector=Input(
                        self.settings_group.component_unique_id(
                            SharedSettingsGroup.Ids.POWER_SELECTOR
                        ).to_string(),
                        "value",
                    ),
                ),
            ),
            ExampleWlfPlugin.Ids.PLOT_VIEW,
        )
        self.add_view(
            TableView(
                self.data,
                TableView.Slots(
                    kindness_selector=Input(
                        self.settings_group.component_unique_id(
                            SharedSettingsGroup.Ids.KINDNESS_SELECTOR
                        ).to_string(),
                        "value",
                    ),
                    power_selector=Input(
                        self.settings_group.component_unique_id(
                            SharedSettingsGroup.Ids.POWER_SELECTOR
                        ).to_string(),
                        "value",
                    ),
                ),
            ),
            ExampleWlfPlugin.Ids.TABLE_VIEW,
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

from typing import List

from dash import Input

from webviz_config import WebvizPluginABC
from webviz_config.utils import StrEnum
from ._views._plot import (
    PlotView,
    PlotViewElement,
    PlotViewSettingsGroup,
    PlotViewElementSettingsGroup,
)
from ._views._table import TableView, TableViewElement, TableViewSettingsGroup
from ._shared_view_elements import TextViewElement
from ._shared_settings import SharedSettingsGroup


class ExampleWlfPlugin(WebvizPluginABC):
    class Ids(StrEnum):
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
                    SharedSettingsGroup.Ids.POWER_SELECTOR
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
                "id": self.view(ExampleWlfPlugin.Ids.PLOT_VIEW)
                .view_element(PlotView.Ids.PLOT)
                .settings_group(PlotViewElement.Ids.PLOT_SETTINGS)
                .component_unique_id(PlotViewElementSettingsGroup.Ids.COLOR_SELECTOR),
                "content": "You can change here which color you prefer.",
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

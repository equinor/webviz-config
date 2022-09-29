from typing import List

from dash.development.base_component import Component
from dash import html

import webviz_core_components as wcc

from webviz_config.utils import StrEnum
from webviz_config.webviz_plugin_subclasses import SettingsGroupABC

from .._views._plot import Kindness


class SharedSettingsGroup(SettingsGroupABC):
    class Ids(StrEnum):
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
                                "label": a.value,
                                "value": a.value,
                            }
                            for a in Kindness
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
                                "value": 2,
                            },
                            {
                                "label": "3",
                                "value": 3,
                            },
                        ],
                        value=2,
                    ),
                ]
            )
        ]

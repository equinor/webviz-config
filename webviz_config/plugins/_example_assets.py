from pathlib import Path

import dash_html_components as html

from .. import WebvizPluginABC
from ..webviz_assets import WEBVIZ_ASSETS


class ExampleAssets(WebvizPluginABC):
    def __init__(self, picture_path: Path):
        super().__init__()

        self.asset_url = WEBVIZ_ASSETS.add(picture_path)

    @property
    def layout(self):
        return html.Img(src=self.asset_url)

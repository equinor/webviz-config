from pathlib import Path

import dash_html_components as html

from .. import WebvizContainerABC
from ..webviz_assets import WEBVIZ_ASSETS


class ExampleAssets(WebvizContainerABC):
    def __init__(self, picture_path: Path):
        self.asset_url = WEBVIZ_ASSETS.add(picture_path)

    @property
    def layout(self):
        return html.Img(src=self.asset_url)

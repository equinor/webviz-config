from pathlib import Path

import dash_html_components as html

from .. import WebvizPluginABC
from ..webviz_assets import WEBVIZ_ASSETS


class ExampleAssets(WebvizPluginABC):
    def __init__(self, picture_path: Path, css_path: Path = None, js_path: Path = None):
        super().__init__()

        self.asset_url = WEBVIZ_ASSETS.add(picture_path)

        if css_path is not None:
            WEBVIZ_ASSETS.add(css_path)

        if js_path is not None:
            WEBVIZ_ASSETS.add(js_path)

    @property
    def layout(self) -> html.Img:
        return html.Img(src=self.asset_url)

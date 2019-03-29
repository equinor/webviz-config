import dash_html_components as html
from pathlib import Path
from ..webviz_assets import webviz_assets


class ExampleAssets:

    def __init__(self, app, picture_path: Path):
        self.asset_url = webviz_assets.add(picture_path)

    @property
    def layout(self):
        return html.Img(src=self.asset_url)

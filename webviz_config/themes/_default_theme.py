import glob
import pathlib

from plotly.io import templates

from webviz_config import WebvizConfigTheme

default_theme = WebvizConfigTheme(theme_name="default")

default_theme.assets = glob.glob(
    str(pathlib.Path(__file__).resolve().parent / "default_assets" / "*")
)
default_theme.assets.append(
    str(
        pathlib.Path(__file__).resolve().parent.parent
        / "_docs"
        / "static"
        / "webviz-logo.svg"
    )
)

default_theme.plotly_theme = templates["plotly"].to_plotly_json()

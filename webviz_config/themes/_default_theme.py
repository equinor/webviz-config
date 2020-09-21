import glob
import pathlib

from plotly.io import templates

from webviz_config import WebvizConfigTheme

default_theme = WebvizConfigTheme(theme_name="default")  # pylint: disable=invalid-name

default_theme.assets = glob.glob(
    str(pathlib.Path(__file__).resolve().parent / "default_assets" / "*")
)

default_theme.plotly_theme = templates["plotly"].to_plotly_json()

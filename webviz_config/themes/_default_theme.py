import os
import glob

from plotly.io import templates

from webviz_config import WebvizConfigTheme

default_theme = WebvizConfigTheme(theme_name="default")  # pylint: disable=invalid-name

default_theme.assets = glob.glob(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_assets", "*")
)

default_theme.plotly_theme = templates["plotly"].to_plotly_json()

import os
import glob
from webviz_config.themes import WebvizConfigTheme

default_theme = WebvizConfigTheme(theme_name='default')

default_theme.assets = glob.glob(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'default_assets',
    '*')
)

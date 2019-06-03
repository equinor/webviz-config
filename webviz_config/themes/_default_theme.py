import os
import glob
from webviz_config.themes import WebvizConfigTheme

default_theme = WebvizConfigTheme(theme_name='default')

default_theme.assets = glob.glob(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'default_assets',
    '*')
)

default_theme.plotly_layout = {
    'paper_bgcolor': 'rgba(90, 90, 90)',
    'plot_bgcolor': 'rgba(90, 90, 90)',
    'colorway': ['#14213d',
                 '#3a2d58',
                 '#69356a',
                 '#9a3a6f',
                 '#c84367',
                 '#ea5954',
                 '#fe7c37',
                 '#ffa600']
    }

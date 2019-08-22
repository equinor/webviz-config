from os import path
import sys
import subprocess
import dash
from webviz_config.common_cache import cache
from webviz_config.webviz_store import webviz_storage
from webviz_config.webviz_assets import webviz_assets
from webviz_config.containers import _example_container


def test_portable(dash_duo):
    subprocess.call(['webviz', 'build', 'basic_example.yaml', '--portable', 'testapp'], cwd='examples')
    fn = path.dirname(__file__) + '/../examples/testapp/webviz_app.py'
    with open(fn, "r") as f:
        lines = f.readlines()
    with open(fn, "w") as f:
        for line in lines:
            if not line.strip("\n").startswith("Talisman"):
                f.write(line)
    sys.path.append(path.dirname(__file__) + '/../examples/testapp')
    import webviz_app
    app = dash.Dash(__name__, external_stylesheets=[])
    app = webviz_app.app

    dash_duo.start_server(app)
    import time
    for page in ['markdown_example', 'table_example', 'pdf_example',
                 'syntax_highlighting_example', 'plot_a_table', 'last_page']:
        dash_duo.wait_for_element(f'#{page}').click()
    assert dash_duo.get_logs() == [], 'browser console should contain no error'
    subprocess.call(['rm', '-rf', 'testapp'], cwd='examples')

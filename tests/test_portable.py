from os import path
import sys
import subprocess
import dash

def test_portable(dash_duo):
    #Build a portable webviz from config file
    subprocess.call(['webviz', 'build', 'basic_example.yaml', '--portable', 'testapp'], cwd='examples')
    fn = path.dirname(__file__) + '/../examples/testapp/webviz_app.py'

    #Remove Talisman
    with open(fn, "r") as f:
        lines = f.readlines()
    with open(fn, "w") as f:
        for line in lines:
            if not line.strip("\n").startswith("Talisman"):
                f.write(line)
    sys.path.append(path.dirname(__file__) + '/../examples/testapp')

    #Import and test portable app
    import webviz_app
    app = dash.Dash(__name__, external_stylesheets=[])
    app = webviz_app.app
    dash_duo.start_server(app)
    for page in ['markdown_example', 'table_example', 'pdf_example',
                 'syntax_highlighting_example', 'plot_a_table', 'last_page']:
        dash_duo.wait_for_element(f'#{page}').click()
    assert dash_duo.get_logs() == [], 'browser console should contain no error'
    subprocess.call(['rm', '-rf', 'testapp'], cwd='examples')

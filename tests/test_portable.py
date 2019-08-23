import sys
import subprocess


def test_portable(dash_duo, tmp_path):
    # Build a portable webviz from config file
    appdir = tmp_path / 'app'
    subprocess.call(['webviz', 'build', 'basic_example.yaml',
                     '--portable', appdir], cwd='examples')
    # Remove Talisman
    fn = appdir / 'webviz_app.py'
    with open(fn, "r") as f:
        lines = f.readlines()
    with open(fn, "w") as f:
        for line in lines:
            if not line.strip("\n").startswith("Talisman"):
                f.write(line)
    # Import generated app
    sys.path.append(str(appdir))
    from webviz_app import app
    # Start and test app
    dash_duo.start_server(app)
    for page in ['markdown_example', 'table_example', 'pdf_example',
                 'syntax_highlighting_example', 'plot_a_table', 'last_page']:
        dash_duo.wait_for_element(f'#{page}').click()
    assert dash_duo.get_logs() == [], 'browser console should contain no error'

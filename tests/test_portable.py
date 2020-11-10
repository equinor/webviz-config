import sys
import subprocess  # nosec


def test_portable(dash_duo, tmp_path):
    # Build a portable webviz from config file
    appdir = tmp_path / "app"
    subprocess.call(  # nosec
        ["webviz", "build", "basic_example.yaml", "--portable", appdir], cwd="examples"
    )

    # Remove Talisman
    filename = appdir / "webviz_app.py"
    with open(filename, "r") as filehandle:
        lines = filehandle.readlines()
    with open(filename, "w") as filehandle:
        for line in lines:
            if not line.strip("\n").startswith("Talisman"):
                filehandle.write(line)

    # Import generated app
    sys.path.append(str(appdir))
    from webviz_app import app  # pylint: disable=import-error, import-outside-toplevel

    # Start and test app
    dash_duo.start_server(app)
    for page in [
        "markdown-example",
        "table-example",
        "pdf-example",
        "syntax-highlighting-example",
        "plot-a-table",
        "pivot-table",
    ]:
        dash_duo.wait_for_element(f"#{page}").click()
    assert dash_duo.get_logs() == [], "browser console should contain no error"

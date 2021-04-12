import sys
import json
import subprocess  # nosec


def _stringify_object_id(uuid) -> str:
    """Object ids must be sorted and converted to
    CSS strings to be recognized as DOM elements"""
    sorted_uuid_obj = json.loads(
        json.dumps(
            uuid,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    string = ["{"]
    for idx, (key, value) in enumerate(sorted_uuid_obj.items()):
        string.append(f'\\"{key}\\"\\:\\"{value}\\"\\')
        if idx == len(sorted_uuid_obj) - 1:
            string.append("}")
        else:
            string.append(",")
    return ("").join(string)


def test_portable(dash_duo, tmp_path):
    # Build a portable webviz from config file
    appdir = tmp_path / "app"
    subprocess.call(  # nosec
        ["webviz", "build", "basic_example.yaml", "--portable", appdir], cwd="examples"
    )

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
        dash_duo.wait_for_element_by_id(
            _stringify_object_id(
                {"id": page, "type": "webviz_config_main_sidebar_link"}
            )
        ).click()
    assert dash_duo.get_logs() == [], "browser console should contain no error"

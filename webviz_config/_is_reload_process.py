import os


def is_reload_process() -> bool:
    """Within the flask reload machinery, it is not straight forward to know
    if the code is run as the main process (i.e. the process the user directly
    started), or if the code is a "hot reload process" (see Flask
    documentation).

    This utility function will use the fact that the reload process
    sets an environment variable WERKZEUG_RUN_MAIN.
    """

    return os.environ.get("WERKZEUG_RUN_MAIN") == "true"

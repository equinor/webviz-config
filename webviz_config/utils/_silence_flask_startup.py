from typing import Any

import flask


def silence_flask_startup() -> None:
    # pylint: disable=line-too-long
    """Calling this function monkey patches the function flask.cli.show_server_banner
    (https://github.com/pallets/flask/blob/a3f07829ca03bf312b12b3732e917498299fa82d/src/flask/cli.py#L657-L683)
    which by default outputs something like:

     * Serving Flask app "webviz_app" (lazy loading)
     * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: off

    This warning is confusing to new users of flask and webviz-config, which thinks
    something is wrong (even though having development/debug mode turned off, and
    limit availability to localhost, is best practice wrt. security).

    After calling this function the exact lines above are not shown
    (all other information/output from the flask instance is untouched).
    """

    def silent_function(*_args: Any, **_kwargs: Any) -> None:
        pass

    flask.cli.show_server_banner = silent_function

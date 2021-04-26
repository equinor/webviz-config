import shutil
import pathlib
import tempfile
import argparse
import logging

import flask

import webviz_config.utils
from ._build_docs import build_docs


def _start_doc_app(build_directory: pathlib.Path) -> None:

    app = flask.Flask(__name__, static_folder=str(build_directory), static_url_path="")
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    @app.route("/")
    def _index() -> str:
        return (build_directory / "index.html").read_text()

    webviz_config.utils.silence_flask_startup()
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    port = webviz_config.utils.get_available_port(preferred_port=5050)
    token = webviz_config.LocalhostToken(app, port).one_time_token
    webviz_config.utils.LocalhostOpenBrowser(port, token)

    app.run(
        host="localhost",
        port=port,
        debug=False,
    )


def open_docs(args: argparse.Namespace) -> None:

    if args.portable is None:
        build_directory = pathlib.Path(tempfile.mkdtemp())
    else:
        build_directory = args.portable.resolve()
        if build_directory.exists():
            if not args.force:
                raise ValueError(
                    f"{build_directory} already exists. Either add --force or change output folder."
                )
            shutil.rmtree(build_directory)
        build_directory.mkdir(parents=True)

    try:
        build_docs(build_directory)
        if not args.skip_open:
            _start_doc_app(build_directory)
    finally:
        if args.portable is None:
            shutil.rmtree(build_directory)

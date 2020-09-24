import sys
import time
import shutil
import pathlib
import tempfile
import subprocess  # nosec
import argparse

from yaml import YAMLError

from ._config_parser import ParserError
from ._write_script import write_script
from .themes import installed_themes
from .utils import terminal_colors

BUILD_FILENAME = "webviz_app.py"
STATIC_FOLDER = pathlib.Path(__file__).resolve().parent / "static"


def build_webviz(args: argparse.Namespace) -> None:

    if args.theme not in installed_themes:
        raise ValueError(f"Theme `{args.theme}` is not installed.")

    if args.portable is None:
        build_directory = pathlib.Path(tempfile.mkdtemp())
    else:
        build_directory = args.portable.resolve()
        build_directory.mkdir(parents=True)

    shutil.copytree(STATIC_FOLDER / "assets", build_directory / "assets")

    for filename in ["README.md", "Dockerfile", ".dockerignore"]:
        shutil.copy(STATIC_FOLDER / filename, build_directory)

    for asset in installed_themes[args.theme].assets:
        shutil.copy(asset, build_directory / "assets")

    (build_directory / "theme_settings.json").write_text(
        installed_themes[args.theme].to_json()
    )

    try:
        if args.portable:
            print(
                f"{terminal_colors.BLUE}{terminal_colors.BOLD}"
                "Saving requested data to build folder "
                "such that the webviz instance is portable."
                f"{terminal_colors.END}"
            )

            write_script(
                args, build_directory, "copy_data_template.py.jinja2", "copy_data.py"
            )

            if subprocess.call(  # nosec
                [sys.executable, "copy_data.py"], cwd=build_directory
            ):
                raise RuntimeError(
                    "Something went wrong. This is probably "
                    "not related to the webviz plugin framework, but more "
                    "likely one of the included plugins in your configuration. "
                    "See exact error message and traceback above."
                )

            (build_directory / "copy_data.py").unlink()

            print(
                f"{terminal_colors.GREEN}{terminal_colors.BOLD}"
                "Finished data extraction. All output saved."
                f"{terminal_colors.END}"
            )

        non_default_assets = write_script(
            args, build_directory, "webviz_template.py.jinja2", BUILD_FILENAME
        )

        for asset in non_default_assets:
            shutil.copy(asset, build_directory / "assets")

        if not args.portable:
            run_webviz(args, build_directory)

    finally:
        if not args.portable:
            shutil.rmtree(build_directory)


def run_webviz(args: argparse.Namespace, build_directory: pathlib.Path) -> None:

    print(
        f"{terminal_colors.YELLOW}"
        " Starting up your webviz application. Please wait..."
        f"{terminal_colors.END}"
    )

    app_process = subprocess.Popen(  # nosec
        [sys.executable, BUILD_FILENAME], cwd=build_directory
    )

    lastmtime = args.yaml_file.stat().st_mtime

    while app_process.poll() is None:
        try:
            time.sleep(1)

            if lastmtime != args.yaml_file.stat().st_mtime:
                lastmtime = args.yaml_file.stat().st_mtime
                write_script(
                    args, build_directory, "webviz_template.py.jinja2", BUILD_FILENAME
                )
                print(
                    f"{terminal_colors.BLUE}{terminal_colors.BOLD}"
                    " Rebuilt webviz dash app from configuration file"
                    f"{terminal_colors.END}"
                )

        except (ParserError, YAMLError) as excep:
            print(
                f"{excep} {terminal_colors.RED}{terminal_colors.BOLD}"
                "Fix the error and save the configuration file in "
                " order to trigger a new rebuild."
                f"{terminal_colors.END}"
            )

        except KeyboardInterrupt:
            app_process.kill()
            print(
                f"\r{terminal_colors.BLUE}{terminal_colors.BOLD}"
                " Shutting down the webviz application on user request."
                f"{terminal_colors.END}"
            )
            app_process.wait()

        except Exception as excep:
            app_process.kill()
            print(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                "Unexpected error. Killing the webviz application process."
                f"{terminal_colors.END}"
            )
            app_process.wait()
            raise excep

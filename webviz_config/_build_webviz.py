import os
import time
import shutil
import tempfile
import subprocess  # nosec

from yaml import YAMLError

from ._config_parser import ParserError
from ._write_script import write_script
from .themes import installed_themes
from .utils import terminal_colors

BUILD_FILENAME = "webviz_app.py"
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "static")


def build_webviz(args):

    if args.theme not in installed_themes:
        raise ValueError(f"Theme `{args.theme}` is not installed.")

    if args.portable is None:
        build_directory = tempfile.mkdtemp()
    else:
        build_directory = args.portable
        os.makedirs(build_directory)

    shutil.copytree(
        os.path.join(STATIC_FOLDER, "assets"), os.path.join(build_directory, "assets")
    )

    for filename in ["README.md", "Dockerfile", ".dockerignore"]:
        shutil.copy(os.path.join(STATIC_FOLDER, filename), build_directory)

    for asset in installed_themes[args.theme].assets:
        shutil.copy(asset, os.path.join(build_directory, "assets"))

    with open(os.path.join(build_directory, "theme_settings.json"), "w") as filehandle:
        filehandle.write(installed_themes[args.theme].to_json())

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
                ["python3", "copy_data.py"], cwd=build_directory
            ):
                raise RuntimeError(
                    "Something went wrong. This is probably "
                    "not related to webviz-config, but more "
                    "likely in one of the  dependencies used "
                    "by one or more containers. See exact "
                    "error message and traceback above"
                )

            os.remove(os.path.join(build_directory, "copy_data.py"))

            print(
                f"{terminal_colors.GREEN}{terminal_colors.BOLD}"
                "Finished data extraction. All output saved."
                f"{terminal_colors.END}"
            )

        non_default_assets = write_script(
            args, build_directory, "webviz_template.py.jinja2", BUILD_FILENAME
        )

        for asset in non_default_assets:
            shutil.copy(asset, os.path.join(build_directory, "assets"))

        if not args.portable:
            run_webviz(args, build_directory)

    finally:
        if not args.portable:
            print(f"Deleting temporary folder {build_directory}")
            shutil.rmtree(build_directory)


def run_webviz(args, build_directory):

    print(
        f"{terminal_colors.YELLOW}"
        " Starting up your webviz application. Please wait..."
        f"{terminal_colors.END}"
    )

    app_process = subprocess.Popen(  # nosec
        ["python3", BUILD_FILENAME], cwd=build_directory
    )

    lastmtime = os.path.getmtime(args.yaml_file)

    while app_process.poll() is None:
        time.sleep(1)

        try:
            if lastmtime != os.path.getmtime(args.yaml_file):
                lastmtime = os.path.getmtime(args.yaml_file)
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

        except Exception as excep:
            app_process.kill()
            print(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                "Unexpected error. Killing the webviz dash application process."
                f"{terminal_colors.END}"
            )
            raise excep

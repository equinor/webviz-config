import sys
import json
import shutil
import logging
import argparse
import pathlib
import subprocess

from ._user_data_dir import user_data_dir
from ._user_preferences import set_user_preferences, get_user_preference


def main() -> None:  # pylint: disable=too-many-locals,too-many-statements

    parser = argparse.ArgumentParser(
        prog=("Creates a Webviz Dash app from a configuration setup")
    )

    subparsers = parser.add_subparsers(
        metavar="SUBCOMMAND",
        required=True,
        help="Below are the available subcommands listed. "
        "Type e.g. 'webviz build --help' "
        "to get help on one particular "
        "subcommand.",
    )

    # Add "build" argument parser:

    parser_build = subparsers.add_parser("build", help="Build a Webviz Dash App")

    parser_build.add_argument(
        "yaml_file", type=pathlib.Path, help="Path to YAML configuration file"
    )
    parser_build.add_argument(
        "--portable",
        type=pathlib.Path,
        default=None,
        metavar="OUTPUTFOLDER",
        help="A portable webviz instance will created "
        "and saved to the given folder.",
    )
    parser_build.add_argument(
        "--theme",
        type=str,
        default=get_user_preference("theme")
        if get_user_preference("theme") is not None
        else "default",
        help="Which installed theme to use.",
    )
    parser_build.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        type=str,
        help="Wanted level of logging output from webviz plugins. "
        "Selecting e.g. INFO will show all log events of level INFO or higher "
        "(WARNING, ERROR and CRITICAL). Default level is WARNING.",
    )
    parser_build.add_argument(
        "--debug",
        action="store_true",
        help="Enable underlying Dash debug tools "
        "(UI with callback graph and errors, use development JavaScript "
        "bundles, validate types/values given to Dash component props).",
    )
    parser_build.add_argument(
        "--logconfig",
        type=pathlib.Path,
        default=None,
        metavar="CONFIGFILE",
        help="Path to YAML file with logging configuration.",
    )

    def parser_build_function(args: argparse.Namespace) -> None:
        from ._build_webviz import (  # pylint: disable=import-outside-toplevel
            build_webviz,
        )

        build_webviz(args)

    parser_build.set_defaults(func=parser_build_function)

    # Add "certificate" parser:

    parser_cert = subparsers.add_parser(
        "certificate",
        help="Create a https certificate authority for webviz "
        "(validity limited to localhost only)",
    )

    parser_cert.add_argument(
        "--force",
        action="store_true",
        help="Overwrite webviz root https certificate if it already exists",
    )

    parser_cert.add_argument(
        "--auto-install",
        action="store_true",
        help="Automatically install the webviz certificate in "
        "your personal public key infrastructure",
    )

    parser_cert.set_defaults(func=_dummy_create_ca)

    # Add "deploy" parser:

    parser_deploy = subparsers.add_parser(
        "deploy",
        help="Facilitates deployment of a portable Webviz application",
    )

    deployment_subparsers = parser_deploy.add_subparsers(
        metavar="DEPLOYMENT_METHOD",
        required=True,
        help="Below are the available deployment subcommands listed. "
        "Type e.g. 'webviz deploy radix --help' "
        "to get help on one particular "
        "subcommand.",
    )

    parser_radix_deploy = deployment_subparsers.add_parser(
        "radix",
        help="Deploy the app using Radix.",
    )

    parser_radix_deploy.add_argument(
        "portable_app",
        type=pathlib.Path,
        help="Path to portable Webviz application folder",
    )

    parser_radix_deploy.add_argument(
        "github_slug",
        type=str,
        help="GitHub slug (i.e. the string 'owner/repo_name').",
    )

    parser_radix_deploy.add_argument(
        "--initial-deploy",
        action="store_true",
        help="Add this flag when setting up a new up application for the first time. "
        "Do not include this if only overwriting an existing application.",
    )

    def parser_radix_deploy_function(args: argparse.Namespace) -> None:
        from ._deployment import (  # pylint: disable=import-outside-toplevel
            main_radix_deployment,
        )

        main_radix_deployment(args)

    parser_radix_deploy.set_defaults(func=parser_radix_deploy_function)

    # Add "documentation" parser:

    parser_docs = subparsers.add_parser(
        "docs",
        help="Get documentation on installed Webviz plugins",
    )

    parser_docs.add_argument(
        "--portable",
        type=pathlib.Path,
        default=None,
        metavar="OUTPUTFOLDER",
        help="Build documentation in given folder, "
        "which then can be deployed directly to e.g. GitHub pages.",
    )

    parser_docs.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output (this flag "
        "only has effect if --portable is given)",
    )

    parser_docs.add_argument(
        "--skip-open",
        action="store_true",
        help="Skip opening the documentation automatically in browser.",
    )

    def parser_docs_function(args: argparse.Namespace) -> None:
        from ._docs.open_docs import (  # pylint: disable=import-outside-toplevel
            open_docs,
        )

        open_docs(args)

    parser_docs.set_defaults(func=parser_docs_function)

    # Add "preferences" parser:

    parser_preferences = subparsers.add_parser(
        "preferences",
        help="Set preferred webviz settings",
    )

    parser_preferences.add_argument(
        "--browser",
        type=str,
        help="Set the name of your preferred browser, "
        "in which localhost applications will open automatically.",
    )
    parser_preferences.add_argument(
        "--theme",
        type=str,
        help="Set your preferred Webviz theme, which will be used if "
        "'--theme' is not provided as an argument with the 'webviz build' command.",
    )

    def entrypoint_preferences(args: argparse.Namespace) -> None:

        if args.theme is not None:
            set_user_preferences(theme=args.theme)

        if args.browser is not None:
            set_user_preferences(browser=args.browser)

        print(f"Preferred theme: {get_user_preference('theme')}")
        print(f"Preferred browser: {get_user_preference('browser')}")

    parser_preferences.set_defaults(func=entrypoint_preferences)

    # Add "schema" parser:

    parser_schema = subparsers.add_parser(
        "schema",
        help="Create YAML (JSON) schema for webviz configuration "
        "file (including all installed plugins)",
    )

    parser_schema.add_argument(
        "--output",
        type=pathlib.Path,
        default=user_data_dir() / "webviz_schema.json",
        help="Name of output JSON schema file. If not given, "
        "it will be stored in your Webviz application settings folder.",
    )

    def parser_schema_function(args: argparse.Namespace) -> None:
        from ._docs._create_schema import (  # pylint: disable=import-outside-toplevel
            create_schema,
        )

        args.output.write_text(json.dumps(create_schema(), indent=4))
        print(f"Schema written to {args.output}")

    parser_schema.set_defaults(func=parser_schema_function)

    # Add "editor" parser:

    parser_editor = subparsers.add_parser(
        "editor",
        help="Create and edit Webviz configuration files",
    )

    # parser_editor.add_argument(
    #     "--path",
    #     type=pathlib.Path,
    #     help="Path to already existing Webviz configuration file.",
    # )

    def entrypoint_editor(  # pylint: disable=unused-argument
        args: argparse.Namespace,
    ) -> None:

        if sys.version_info < (3, 8):
            raise RuntimeError("Webviz editor requires at least Python 3.8")

        path_wce_executable = shutil.which("webviz-config-editor")
        if path_wce_executable is None:
            raise RuntimeError(
                "webviz-config-editor executable not found. You can download this from "
                "release assets (https://github.com/equinor/webviz-config-editor/releases)."
            )

        logging.warning(
            "Note that Webviz editor is in beta and early testing. "
            "Problems/bugs likely to occur."
        )

        command = [path_wce_executable]  # + ([] if args.path is None else [args.path])
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            subprocess.run(command + ["--no-sandbox"], check=True)

    parser_editor.set_defaults(func=entrypoint_editor)

    # Do the argument parsing:

    args = parser.parse_args()

    args.func(args)


def _dummy_create_ca(_args: argparse.Namespace) -> None:
    """
    Print out a message about certs being unnecessary and exit gracefully (ie.
    returncode 0)
    """
    print(
        "The 'certificate' command is no longer needed as Webviz uses HTTP for local servers"
    )
    sys.exit(0)

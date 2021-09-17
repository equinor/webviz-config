import sys
import json
import argparse
import pathlib

from ._build_webviz import build_webviz
from ._deployment import main_radix_deployment
from ._docs.open_docs import open_docs
from ._docs._create_schema import create_schema
from ._user_data_dir import user_data_dir
from ._user_preferences import set_user_preferences, get_user_preference


def main() -> None:

    parser = argparse.ArgumentParser(
        prog=("Creates a Webviz Dash app from a configuration setup")
    )

    subparsers = parser.add_subparsers(
        metavar="SUBCOMMAND",
        help="Below are the available subcommands listed. "
        "Type e.g. 'webviz build --help' "
        "to get help on one particular "
        "subcommand.",
    )
    # When dropping Python 3.6 support, 'required' can be given as an argument to add_subparsers.
    subparsers.required = True

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

    parser_build.set_defaults(func=build_webviz)

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
        help="Below are the available deployment subcommands listed. "
        "Type e.g. 'webviz deploy radix --help' "
        "to get help on one particular "
        "subcommand.",
    )

    # When dropping Python 3.6 support, 'required' can be given as an argument to add_subparsers.
    deployment_subparsers.required = True

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

    parser_radix_deploy.set_defaults(func=main_radix_deployment)

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

    parser_docs.set_defaults(func=open_docs)

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

    def entrypoint_schema(args: argparse.Namespace) -> None:
        args.output.write_text(json.dumps(create_schema(), indent=4))
        print(f"Schema written to {args.output}")

    parser_schema.set_defaults(func=entrypoint_schema)

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

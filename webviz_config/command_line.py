import json
import argparse
import pathlib

from ._build_webviz import build_webviz
from .certificate._certificate_generator import create_ca
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

    parser_cert.set_defaults(func=create_ca)

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

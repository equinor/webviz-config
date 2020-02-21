import argparse

from ._build_webviz import build_webviz
from .certificate._certificate_generator import create_ca
from ._user_preferences import set_user_preferences, get_user_preference


def main() -> None:

    parser = argparse.ArgumentParser(
        prog=("Creates a Webviz Dash app from a configuration setup")
    )

    subparsers = parser.add_subparsers(
        help="The options available. "
        'Type e.g. "webviz build --help" '
        "to get help on that particular "
        "option."
    )

    # Add "build" argument parser:

    parser_build = subparsers.add_parser("build", help="Build a Webviz Dash App")

    parser_build.add_argument(
        "yaml_file", type=str, help="Path to YAML configuration file"
    )
    parser_build.add_argument(
        "--portable",
        type=str,
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

    # Add "preferences" parser:

    parser_preferences = subparsers.add_parser(
        "preferences", help="Set preferred webviz settings",
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

    # Do the argument parsing:

    args = parser.parse_args()

    args.func(args)

import argparse
from ._build_webviz import build_webviz
from ._certificate import create_ca


def main():

    parser = argparse.ArgumentParser(prog=('Creates a Webviz Dash app '
                                           'from a configuration setup'))

    subparsers = parser.add_subparsers(help='The options available. '
                                            'Type e.g. "webviz build --help" '
                                            'to get help on that particular '
                                            'option.')

    # Add "build" argument parser:

    parser_build = subparsers.add_parser('build', help='Build a Webviz '
                                                       'Dash App')

    parser_build.add_argument('yaml_file', type=str,
                              help='Path to YAML configuration file')
    parser_build.add_argument('--portable', type=str, default=None,
                              metavar='OUTPUTFOLDER',
                              help='A portable webviz instance will created '
                                   'and saved to the given folder.')
    parser_build.add_argument('--not-only-localhost', action='store_true',
                              help='Front-end accesible on internal network')
    parser_build.add_argument('--debug', action='store_true',
                              help='Start the application in debug mode')
    parser_build.add_argument('--theme', type=str, default='default',
                              help='Which installed theme to use.')

    def check_port(port):
        port = int(port)
        if port <= 1024:
            argparse.ArgumentTypeError('Port must be greater than 1024')
        return port

    parser_build.add_argument('--port', type=check_port, default=8050,
                              help='Port to use for the server.')

    parser_build.set_defaults(func=build_webviz)

    # Add "certificate" parser:

    parser_cert = subparsers.add_parser('certificate', help='Create a root '
                                                            'certificate '
                                                            'for https')

    parser_cert.add_argument('--force', action='store_true',
                             help='Overwrite webviz root https '
                                  'certificate if it already exist')

    parser_cert.set_defaults(func=create_ca)

    # Do the argument parsing:

    args = parser.parse_args()

    args.func(args)

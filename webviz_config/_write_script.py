import os
import jinja2
from .themes import installed_themes
from ._config_parser import ConfigParser
from ._certificate import create_certificate, SERVER_KEY_FILENAME, \
                          SERVER_CRT_FILENAME


def write_script(args, build_directory, template_filename, output_filename):

    config_parser = ConfigParser(args.yaml_file)
    configuration = config_parser.configuration

    configuration['port'] = args.port
    configuration['portable'] = True if args.portable else False
    configuration['localhostonly'] = not args.not_only_localhost

    theme = installed_themes[args.theme]
    configuration['csp'] = theme.csp
    configuration['feature_policy'] = theme.feature_policy
    configuration['external_stylesheets'] = theme.external_stylesheets
    configuration['plotly_layout'] = theme.plotly_layout

    configuration['ssl_context'] = '({!r}, {!r})'\
                                   .format(SERVER_CRT_FILENAME,
                                           SERVER_KEY_FILENAME)

    create_certificate(build_directory)

    template_environment = jinja2.Environment(
                 loader=jinja2.PackageLoader('webviz_config', 'templates'),
                 undefined=jinja2.StrictUndefined
                )

    template = template_environment.get_template(template_filename)

    with open(os.path.join(build_directory, output_filename), 'w') as fh:
        fh.write(template.render(configuration))

    return config_parser.assets

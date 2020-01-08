import os
import getpass
import datetime
import pathlib

import jinja2

from ._config_parser import ConfigParser


def write_script(args, build_directory, template_filename, output_filename):

    config_parser = ConfigParser(args.yaml_file)
    configuration = config_parser.configuration

    configuration["shared_settings"] = config_parser.shared_settings
    configuration["portable"] = args.portable is not None
    configuration["config_folder"] = repr(pathlib.Path(args.yaml_file).resolve().parent)

    configuration["theme_name"] = args.theme

    configuration["author"] = getpass.getuser()
    configuration["current_date"] = datetime.date.today().strftime("%Y-%m-%d")

    template_environment = jinja2.Environment(  # nosec
        loader=jinja2.PackageLoader("webviz_config", "templates"),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )

    template = template_environment.get_template(template_filename)

    with open(os.path.join(build_directory, output_filename), "w") as filehandle:
        filehandle.write(template.render(configuration))

    return config_parser.assets

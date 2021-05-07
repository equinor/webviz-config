import sys
import getpass
import datetime
import pathlib
import argparse
from typing import Dict, Tuple

import yaml
import jinja2

from ._config_parser import ConfigParser


def write_script(
    args: argparse.Namespace,
    build_directory: pathlib.Path,
    template_filename: str,
    output_filename: str,
) -> Tuple[set, Dict[str, dict]]:
    """Writes rendered script to build directory. Also returns information regarding
    assets and which plugins that are incluced in the user provided configuration file.
    """

    config_parser = ConfigParser(args.yaml_file)
    configuration = config_parser.configuration

    configuration["shared_settings"] = config_parser.shared_settings
    configuration["portable"] = args.portable is not None

    configuration["loglevel"] = args.loglevel

    if args.logconfig is not None:
        configuration["logging_config_dict"] = yaml.safe_load(
            args.logconfig.read_text()
        )

    configuration["config_folder"] = repr(args.yaml_file.resolve().parent)

    configuration["theme_name"] = args.theme

    configuration["author"] = getpass.getuser()
    configuration["current_date"] = datetime.date.today().strftime("%Y-%m-%d")
    configuration["sys_executable"] = sys.executable

    template_environment = jinja2.Environment(  # nosec
        loader=jinja2.PackageLoader("webviz_config", "templates"),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )

    template = template_environment.get_template(template_filename)

    (build_directory / output_filename).write_text(template.render(configuration))

    return config_parser.assets, config_parser.plugin_metadata

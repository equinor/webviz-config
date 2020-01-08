"""Builds automatic documentation of the installed webviz config plugins.
The documentation is designed to be used by the YAML configuration file end
user. Sphinx has not been used due to

 1) Sphinx is geared towards Python end users, and templateing of apidoc output
    is not yet supported (https://github.com/sphinx-doc/sphinx/issues/3545).

 2) It is a small problem to be solved, and most of the Sphinx machinery
    is not needed.

Overall workflow is:
    * Finds all installed plugins.
    * Automatically reads docstring and __init__ function signature (both
      argument names and which arguments have default values).
    * Output the extracted plugin information in html using jinja2.
"""

import shutil
import inspect
import pathlib
from importlib import import_module
from collections import defaultdict
import jinja2
from markdown import markdown
import webviz_config.plugins
from webviz_config._config_parser import SPECIAL_ARGS

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
BUILD_DIR = SCRIPT_DIR / "_build"
TEMPLATE_FILE = SCRIPT_DIR / "templates" / "index.html.jinja2"
EXAMPLE = SCRIPT_DIR / ".." / "examples" / "basic_example.yaml"


def escape_all(input_string):
    """Escapes any html or utf8 character in the given string.
    """

    no_html = jinja2.escape(input_string)
    no_utf8 = no_html.encode("ascii", "xmlcharrefreplace").decode()
    pass_through = jinja2.Markup(no_utf8)
    return pass_through


def convert_docstring(doc):
    """Convert docstring to markdown.
    """

    return "" if doc is None else markdown(doc, extensions=["fenced_code"])


def get_plugin_documentation():
    """Get all installed plugins, and document them by grabbing docstring
    and input arguments / function signature.
    """

    plugins = inspect.getmembers(webviz_config.plugins, inspect.isclass)

    plugin_doc = []

    for plugin in plugins:
        reference = plugin[1]

        plugin_info = {}

        plugin_info["name"] = plugin[0]
        plugin_info["doc"] = convert_docstring(reference.__doc__)

        argspec = inspect.getfullargspec(reference.__init__)
        plugin_info["args"] = [
            arg for arg in argspec.args if arg not in SPECIAL_ARGS
        ]

        plugin_info["values"] = defaultdict(lambda: "some value")

        if argspec.defaults is not None:
            for arg, default in dict(
                zip(reversed(argspec.args), reversed(argspec.defaults))
            ).items():
                plugin_info["values"][
                    arg
                ] = f"{default}  # Optional (default value shown here)."

        module = inspect.getmodule(reference)
        plugin_info["module"] = module.__name__

        package = inspect.getmodule(module).__package__
        plugin_info["package"] = package
        plugin_info["package_doc"] = convert_docstring(
            import_module(package).__doc__
        )

        if not plugin_info["name"].startswith("Example"):
            plugin_doc.append(plugin_info)

    # Sort the plugins by package:

    package_ordered = defaultdict(lambda: {"plugins": []})

    for plugin in sorted(plugin_doc, key=lambda x: (x["module"], x["name"])):
        package = plugin["package"]
        package_ordered[package]["plugins"].append(plugin)
        package_ordered[package]["doc"] = plugin["package_doc"]

    return package_ordered


def get_basic_example():
    with open(EXAMPLE) as fh:
        return escape_all(fh.read())


if __name__ == "__main__":

    template_data = {
        "packages": get_plugin_documentation(),
        "basic_example": get_basic_example(),
    }

    with open(TEMPLATE_FILE) as fh:
        template = jinja2.Template(fh.read())

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    shutil.copytree(SCRIPT_DIR / "assets", BUILD_DIR / "assets")

    with open(BUILD_DIR / "index.html", "w") as fh:
        fh.write(template.render(template_data))

    print(f"Output available in {BUILD_DIR}")

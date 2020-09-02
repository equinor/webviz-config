"""Builds automatic documentation of the installed webviz-config plugins.
The documentation is designed to be used by the YAML configuration file end
user. Sphinx has not been used, as the documentation from Sphinx is geared
mostly towards Python end users. It is also a small task generating `webviz`
documentation, and most of the Sphinx machinery is not needed.

Overall workflow is:
    * Find all installed plugins.
    * Automatically read docstring and __init__ function signatures (both
      argument names and which arguments have default values).
    * Output the extracted plugin information into docsify input using jinja2.
"""

import shutil
import inspect
import pathlib
from importlib import import_module
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple, List

import pkg_resources
import jinja2
from typing_extensions import TypedDict

import webviz_config.plugins
from webviz_config._config_parser import SPECIAL_ARGS


class ArgInfo(TypedDict, total=False):
    required: bool
    default: Any
    typehint: Any
    typehint_string: str


class PluginInfo(TypedDict):
    arg_info: Dict[str, ArgInfo]
    argument_description: Optional[str]
    data_input: Optional[str]
    description: Optional[str]
    module: str
    name: str
    package: str
    package_doc: Optional[str]
    package_version: str


def _document_plugin(plugin: Tuple[str, Any]) -> PluginInfo:
    """Takes in a tuple (from e.g. inspect.getmembers), and returns
    a dictionary according to the type definition PluginInfo.
    """

    name, reference = plugin
    docstring = reference.__doc__ if reference.__doc__ is not None else ""
    docstring_parts = _split_docstring(docstring)
    argspec = inspect.getfullargspec(reference.__init__)
    module = inspect.getmodule(reference)
    subpackage = inspect.getmodule(module).__package__  # type: ignore
    top_package_name = subpackage.split(".")[0]  # type: ignore

    plugin_info: PluginInfo = {
        "arg_info": {arg: {} for arg in argspec.args if arg not in SPECIAL_ARGS},
        "argument_description": docstring_parts[1]
        if len(docstring_parts) > 1
        else None,
        "data_input": docstring_parts[2] if len(docstring_parts) > 2 else None,
        "description": docstring_parts[0] if docstring != "" else None,
        "name": name,
        "module": module.__name__,  # type: ignore
        "package": top_package_name,
        "package_doc": import_module(subpackage).__doc__,  # type: ignore
        "package_version": pkg_resources.get_distribution(top_package_name).version,
    }

    if argspec.defaults is not None:
        for arg, default in dict(
            zip(reversed(argspec.args), reversed(argspec.defaults))
        ).items():
            plugin_info["arg_info"][arg]["default"] = default

    for arg, arg_info in plugin_info["arg_info"].items():
        arg_info["required"] = "default" not in arg_info

    for arg, annotation in argspec.annotations.items():
        if arg not in SPECIAL_ARGS:
            plugin_info["arg_info"][arg]["typehint"] = annotation
            plugin_info["arg_info"][arg]["typehint_string"] = _annotation_to_string(
                annotation
            )

    return plugin_info


def get_plugin_documentation() -> defaultdict:
    """Find all installed webviz plugins, and then document them
    by grabbing docstring and input arguments / function signature.
    """

    plugin_doc = [
        _document_plugin(plugin)
        for plugin in inspect.getmembers(webviz_config.plugins, inspect.isclass)
        if not plugin[0].startswith("Example")
    ]

    # Sort the plugins by package:
    package_ordered: defaultdict = defaultdict(lambda: {"plugins": []})
    for sorted_plugin in sorted(plugin_doc, key=lambda x: (x["module"], x["name"])):
        package = sorted_plugin["package"]
        package_ordered[package]["plugins"].append(sorted_plugin)
        package_ordered[package]["doc"] = sorted_plugin["package_doc"]
        package_ordered[package]["version"] = sorted_plugin["package_version"]

    return package_ordered


def _annotation_to_string(annotation: Any) -> str:
    """Takes in a type annotation (that could come from e.g. inspect.getfullargspec)
    and transforms it into a human readable string.
    """

    def remove_fix(string: str, fix: str, prefix: bool = True) -> str:
        if prefix and string.startswith(fix):
            return string[len(fix) :]
        if not prefix and string.endswith(fix):
            return string[: -len(fix)]
        return string

    text_type = str(annotation)
    text_type = remove_fix(text_type, "typing.")
    text_type = remove_fix(text_type, "<class '")
    text_type = remove_fix(text_type, "'>", prefix=False)
    text_type = text_type.replace("pathlib.Path", "str (corresponding to a path)")

    return text_type


def build_docs(build_directory: pathlib.Path) -> None:

    # From Python 3.8, copytree gets an argument dirs_exist_ok.
    # Then the rmtree command can be removed.
    shutil.rmtree(build_directory)
    shutil.copytree(
        pathlib.Path(__file__).resolve().parent / "static",
        build_directory,
    )

    template_environment = jinja2.Environment(  # nosec
        loader=jinja2.PackageLoader("webviz_config", "templates"),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )

    plugin_documentation = get_plugin_documentation()

    template = template_environment.get_template("README.md.jinja2")
    for package_name, package_doc in plugin_documentation.items():
        (build_directory / (package_name + ".md")).write_text(
            template.render({"package_name": package_name, "package_doc": package_doc})
        )

    template = template_environment.get_template("sidebar.md.jinja2")
    (build_directory / "sidebar.md").write_text(
        template.render({"packages": plugin_documentation.keys()})
    )


def _split_docstring(docstring: str) -> List[str]:
    """Divides docstring by splitting on ---, also unindents
    first in case of indented docstrings (similar to this one)
    """
    lines = docstring.strip().split("\n")

    try:
        indent_spaces = min(
            [len(line) - len(line.lstrip()) for line in lines[1:] if line.strip() != ""]
        )
    except ValueError:  # In the case of no original newline (\n)
        indent_spaces = 0

    unindented_lines = [lines[0]] + [line[indent_spaces:] for line in lines[1:]]
    return "\n".join(unindented_lines).split("\n---\n")

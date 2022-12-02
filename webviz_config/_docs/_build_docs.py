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
from typing import Any, Dict, Optional, Tuple, List, TypedDict

import jinja2

import webviz_config.plugins
from webviz_config.plugins import PLUGIN_METADATA, PLUGIN_PROJECT_METADATA
from .._config_parser import SPECIAL_ARGS
from .. import _deprecation_store as _ds


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
    dist_name: str
    dist_version: str
    name: str
    package_doc: Optional[str]


class ArgumentInfo(TypedDict, total=False):
    description: str
    default_value: str
    required: bool
    typehint: Any
    typehint_string: str
    deprecated: bool
    deprecation_message: str
    deprecation_code: str


def _find_plugin_deprecated_arguments(plugin: Any) -> Dict[str, Tuple[str, str]]:
    deprecated_arguments = (
        _ds.DEPRECATION_STORE.get_stored_plugin_argument_deprecations(plugin.__init__)
    )
    result: Dict[str, Tuple[str, str]] = {}
    for deprecated_argument in deprecated_arguments:
        if isinstance(deprecated_argument, _ds.DeprecatedArgumentCheck):
            for arg in deprecated_argument.argument_names:
                result[arg] = ("", deprecated_argument.callback_code)
    # Completely deprecated arguments have priority over deprecation check functions
    for deprecated_argument in deprecated_arguments:
        if isinstance(deprecated_argument, _ds.DeprecatedArgument):
            result[deprecated_argument.argument_name] = (
                deprecated_argument.long_message,
                "",
            )
    return result


def _extract_init_arguments_and_check_for_deprecation(
    reference: Any,
) -> Tuple[bool, Dict[str, ArgumentInfo], str]:
    """Returns all arguments of the given class' __init__ function including
    related documentation strings, typehints and deprecation information.
    """
    result: Dict[str, ArgumentInfo] = {}
    deprecated_arguments = _find_plugin_deprecated_arguments(reference)
    deprecation_check_code = ""

    argspec = inspect.getfullargspec(reference.__init__)
    result = {arg: ArgumentInfo() for arg in argspec.args if arg not in SPECIAL_ARGS}

    if argspec.defaults is not None:
        for arg, default in dict(
            zip(reversed(argspec.args), reversed(argspec.defaults))
        ).items():
            # Casting pathlib.Path to str could become unnecessary if outsourcing creation
            # of json schema to pydantic https://pydantic-docs.helpmanual.io/
            result[arg]["default_value"] = (
                str(default) if isinstance(default, pathlib.Path) else default
            )

    for arg, arg_info in result.items():
        arg_info["required"] = "default_value" not in arg_info

    for arg, annotation in argspec.annotations.items():
        if arg not in SPECIAL_ARGS and arg != "return":
            result[arg]["typehint"] = annotation
            result[arg]["typehint_string"] = _annotation_to_string(annotation)

    for arg, arg_info in result.items():
        if arg in deprecated_arguments:
            arg_info["deprecated"] = True
            arg_info["deprecation_message"] = deprecated_arguments[arg][0]
            arg_info["deprecation_code"] = deprecated_arguments[arg][1]
            if deprecation_check_code == "" and deprecated_arguments[arg][1] != "":
                deprecation_check_code = deprecated_arguments[arg][1]
        else:
            arg_info["deprecated"] = False

    return (bool(deprecated_arguments), result, deprecation_check_code)


def _document_plugin(plugin_name: str) -> PluginInfo:
    """Takes in plugin name as string and returns
    a dictionary according to the type definition PluginInfo.
    """

    reference = webviz_config.plugins.__getattr__(plugin_name)
    docstring = reference.__doc__ if reference.__doc__ is not None else ""
    docstring_parts = _split_docstring(docstring)
    module = inspect.getmodule(reference)
    subpackage = inspect.getmodule(module).__package__  # type: ignore
    dist_name = PLUGIN_METADATA[plugin_name]["dist_name"]
    (
        has_deprecated_arguments,
        arguments,
        deprecation_check_code,
    ) = _extract_init_arguments_and_check_for_deprecation(reference)
    deprecated = _ds.DEPRECATION_STORE.get_stored_plugin_deprecation(reference)

    plugin_info: PluginInfo = {
        "arg_info": arguments,
        "argument_description": docstring_parts[1]
        if len(docstring_parts) > 1
        else None,
        "data_input": docstring_parts[2] if len(docstring_parts) > 2 else None,
        "description": docstring_parts[0] if docstring != "" else None,
        "name": plugin_name,
        "package_doc": import_module(subpackage).__doc__,  # type: ignore
        "dist_name": dist_name,
        "dist_version": PLUGIN_PROJECT_METADATA[dist_name]["dist_version"],
        "deprecated": deprecated is not None,
        "deprecation_text_short": deprecated.short_message if deprecated else "",
        "deprecation_text_long": deprecated.long_message if deprecated else "",
        "has_deprecated_arguments": has_deprecated_arguments,
        "deprecation_check_code": deprecation_check_code,
    }

    return plugin_info


def get_plugin_documentation() -> defaultdict:
    """Find all installed webviz plugins, and then document them
    by grabbing docstring and input arguments / function signature.
    """

    plugin_doc = [
        _document_plugin(plugin)
        for plugin in webviz_config.plugins.__all__
        if not plugin.startswith("Example")
    ]

    # Sort the plugins by package:
    package_ordered: defaultdict = defaultdict(lambda: {"plugins": []})
    for sorted_plugin in sorted(plugin_doc, key=lambda x: (x["dist_name"], x["name"])):
        package = sorted_plugin["dist_name"]
        package_ordered[package]["plugins"].append(sorted_plugin)
        package_ordered[package]["doc"] = sorted_plugin["package_doc"]
        package_ordered[package]["dist_version"] = sorted_plugin["dist_version"]

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

    has_deprecated_plugins = {}
    has_deprecated_arguments = {}
    for dist_name, package_doc in plugin_documentation.items():
        if any(plugin["deprecated"] for plugin in package_doc["plugins"]):
            has_deprecated_plugins[dist_name] = package_doc
        if any(plugin["has_deprecated_arguments"] for plugin in package_doc["plugins"]):
            has_deprecated_arguments[dist_name] = package_doc
    template = template_environment.get_template("README.md.jinja2")
    for dist_name, package_doc in plugin_documentation.items():
        (build_directory / f"{dist_name}.md").write_text(
            template.render({"dist_name": dist_name, "package_doc": package_doc})
        )

    template = template_environment.get_template("sidebar.md.jinja2")
    (build_directory / "sidebar.md").write_text(
        template.render(
            {
                "packages": plugin_documentation.keys(),
                "deprecated_plugins": bool(has_deprecated_plugins),
                "deprecated_arguments": bool(has_deprecated_arguments),
            }
        )
    )

    template = template_environment.get_template("webviz-doc.js.jinja2")
    (build_directory / "webviz-doc.js").write_text(
        template.render(
            {"paths": ["/"] + [f"/{dist_name}" for dist_name in plugin_documentation]}
        )
    )

    template = template_environment.get_template("plugin_deprecations.md.jinja2")
    (build_directory / "plugin_deprecations.md").write_text(
        template.render({"packages": has_deprecated_plugins})
    )
    template = template_environment.get_template("argument_deprecations.md.jinja2")
    (build_directory / "argument_deprecations.md").write_text(
        template.render({"packages": has_deprecated_arguments})
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

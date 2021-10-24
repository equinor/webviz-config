import re
import sys
import pathlib
import inspect
from typing import Dict, List, Optional, Any
import warnings

import yaml

import webviz_config.plugins
from .utils import terminal_colors
from .utils._get_webviz_plugins import _get_webviz_plugins
from . import _deprecation_store as _ds

SPECIAL_ARGS = ["self", "app", "webviz_settings", "_call_signature"]


def _call_signature(
    plugin_name: str,
    kwargs: dict,
    config_folder: pathlib.Path,
    contact_person: Optional[dict] = None,
) -> tuple:
    # pylint: disable=too-many-branches,too-many-statements,too-many-locals
    """Takes as input the name of a plugin together with user given arguments
    (originating from the configuration file). Returns the equivalent Python code wrt.
    initiating an instance of that plugin (with the given arguments).

    Raises ParserError in the following scenarios:
      * User is missing a required (i.e. no default value) __init__ argument
      * User provided an argument not existing in the class' __init__ function
      * User has given one of the protected arguments in SPECIAL_ARGS
      * If there is type mismatch between user given argument value, and type
        hint in __init__ signature (given that type hint exist)
    """
    argspec = inspect.getfullargspec(
        getattr(webviz_config.plugins, plugin_name).__init__
    )

    if argspec.defaults is not None:
        required_args = argspec.args[: -len(argspec.defaults)]
    else:
        required_args = argspec.args

    for arg in required_args:
        if arg not in SPECIAL_ARGS and arg not in kwargs:
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                f"The plugin `{plugin_name}` requires the argument "
                f"`{arg}` in your configuration file. "
                "Run the command `webviz docs` if you want "
                "to see documentation of the plugin."
                f"{terminal_colors.END}"
            )

    for arg in list(kwargs):
        if arg in SPECIAL_ARGS:
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                f"Argument `{arg}` not allowed."
                f"{terminal_colors.END}"
            )

        if arg == "contact_person":
            if not isinstance(kwargs["contact_person"], dict):
                raise ParserError(
                    f"{terminal_colors.RED}{terminal_colors.BOLD}"
                    f"The contact information provided for "
                    f"`{plugin_name}` is not a dictionary. "
                    f"{terminal_colors.END}"
                )

            if any(
                key not in ["name", "phone", "email"]
                for key in kwargs["contact_person"]
            ):
                raise ParserError(
                    f"{terminal_colors.RED}{terminal_colors.BOLD}"
                    f"Unrecognized contact information key given to `{plugin_name}`. "
                    f"Should be 'name', 'phone' and/or 'email'."
                    f"{terminal_colors.END}"
                )

            contact_person = kwargs.pop("contact_person")

        elif arg not in argspec.args:
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                f"Unrecognized argument. `{plugin_name}` "
                f"does not take an argument `{arg}`. "
                "Run the command `webviz docs` if you want "
                "to see documentation of the plugin."
                f"{terminal_colors.END}"
            )

        if arg in argspec.annotations:
            expected_type = argspec.annotations[arg]

            if expected_type == pathlib.Path:
                kwargs[arg] = (config_folder / pathlib.Path(kwargs[arg])).resolve()
            elif expected_type == List[pathlib.Path]:
                kwargs[arg] = [
                    (config_folder / pathlib.Path(patharg)).resolve()
                    for patharg in kwargs[arg]
                ]
            try:
                if not isinstance(kwargs[arg], expected_type):
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        f"The value provided for argument `{arg}` "
                        f"given to `{plugin_name}` is "
                        f"of type `{type(kwargs[arg]).__name__}`. "
                        f"Expected type "
                        f"`{argspec.annotations[arg].__name__}`. "
                        "Run the command `webviz docs` if you want "
                        "to see documentation of the plugin."
                        f"{terminal_colors.END}"
                    )
            # Typechecking typing classes does not work in python 3.7
            except TypeError:
                pass

    kwargs_including_defaults = kwargs
    plugin_deprecation_warnings = []
    argument_deprecation_warnings = []

    deprecated_plugin = _ds.DEPRECATION_STORE.get_stored_plugin_deprecation(
        getattr(webviz_config.plugins, plugin_name)
    )
    if deprecated_plugin:
        plugin_deprecation_warnings.append(deprecated_plugin.short_message)
        warnings.warn(
            f"""Plugin '{plugin_name}' has been deprecated.
------------------------
{deprecated_plugin.short_message}
===
{deprecated_plugin.long_message}
""",
            FutureWarning,
        )

    deprecations = _ds.DEPRECATION_STORE.get_stored_plugin_argument_deprecations(
        getattr(webviz_config.plugins, plugin_name).__init__
    )

    signature = inspect.signature(getattr(webviz_config.plugins, plugin_name).__init__)
    for key, value in signature.parameters.items():
        if value.default is not inspect.Parameter.empty and key not in kwargs.keys():
            kwargs_including_defaults[key] = value.default

    for deprecation in deprecations:
        if isinstance(deprecation, _ds.DeprecatedArgument):
            if deprecation.argument_name in kwargs_including_defaults.keys():
                argument_deprecation_warnings.append(deprecation.short_message)
                warnings.warn(
                    f"Deprecated Argument: '{deprecation.argument_name}' with value "
                    f"'{kwargs_including_defaults[deprecation.argument_name]}' "
                    f"in plugin '{plugin_name}\n'"
                    "------------------------\n"
                    f"{deprecation.short_message}\n"
                    "===\n"
                    f"{deprecation.long_message}",
                    FutureWarning,
                )
        elif isinstance(deprecation, _ds.DeprecatedArgumentCheck):
            mapped_args: Dict[str, Any] = {}
            for arg in deprecation.argument_names:
                for name, value in kwargs_including_defaults.items():
                    if arg == name:
                        mapped_args[arg] = value
                        break

            result = deprecation.callback(**mapped_args)
            if result:
                argument_deprecation_warnings.append(result[0])
                _values = [
                    value
                    for key, value in kwargs_including_defaults.items()
                    if key in deprecation.argument_names
                ]
                warnings.warn(
                    f"Deprecated Argument(s): '{deprecation.argument_names}' "
                    f"with value(s) '{_values}' in plugin '{plugin_name}'\n"
                    "------------------------\n"
                    f"{result[0]}\n"
                    "===\n"
                    f"{result[1]}",
                    FutureWarning,
                )

    special_args = ""
    if "app" in argspec.args:
        special_args += "app=app, "
    if "webviz_settings" in argspec.args:
        special_args += "webviz_settings=webviz_settings, "

    return (
        f"{plugin_name}({special_args}**{kwargs})",
        (
            f"plugin_layout(contact_person={contact_person}"
            f", plugin_deprecation_warnings={plugin_deprecation_warnings}"
            f", argument_deprecation_warnings={argument_deprecation_warnings})"
        ),
    )


class ParserError(Exception):
    pass


class ConfigParser:

    STANDARD_PLUGINS = [
        name for (name, _) in _get_webviz_plugins(webviz_config.plugins)
    ]

    def __init__(self, yaml_file: pathlib.Path):

        ConfigParser.check_for_tabs_in_file(yaml_file)

        try:
            self._configuration = yaml.safe_load(yaml_file.read_text())
        except yaml.MarkedYAMLError as excep:
            extra_info = (
                f"There is something wrong in the configuration file {yaml_file}. "
            )

            # Looking forward to only supporting Python 3.8+ and PEP572...
            problem_mark = getattr(excep, "problem_mark", None)
            if problem_mark is not None:
                extra_info += (
                    "The typo is probably somewhere around "
                    f"line {problem_mark.line + 1}."
                )

            raise type(excep)(
                f"{excep}. {terminal_colors.RED}{terminal_colors.BOLD}"
                f"{extra_info}{terminal_colors.END}"
            ).with_traceback(sys.exc_info()[2])

        self._config_folder = pathlib.Path(yaml_file).parent
        self._page_ids: List[str] = []
        self._assets: set = set()
        self._plugin_metadata: Dict[str, dict] = {}
        self._used_plugin_packages: set = set()
        self.clean_configuration()

    @staticmethod
    def check_for_tabs_in_file(path: pathlib.Path) -> None:

        line_numbers_with_tabs = sorted(
            list(
                {
                    i + 1
                    for i, line in enumerate(path.read_text().splitlines())
                    if "\t" in line
                }
            )
        )

        if line_numbers_with_tabs:
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                "The configuration file contains tabs. You should use ordinary spaces "
                "instead. The following lines contain tabs:\n"
                f"{', '.join([str(line_no) for line_no in line_numbers_with_tabs])}"
                f"{terminal_colors.END}"
            )

    def _generate_page_id(self, title: str) -> str:
        """From the user given title, this function provides a unique
        human readable page id, not already present in `self._page_ids`.
        """

        base_id = re.sub("[^-a-z0-9_]+", "", title.lower().replace(" ", "-"))

        page_id = base_id

        count = 1
        while page_id in self._page_ids:
            count += 1
            page_id = f"{base_id}{count}"

        return page_id

    def clean_configuration(self) -> None:
        """Various cleaning and checks of the raw configuration read
        from the user provided yaml configuration file.
        """

        self.configuration["_imports"] = set()

        if "shared_settings" in self.configuration:
            self._shared_settings = self.configuration["shared_settings"]
        else:
            self._shared_settings = {}

        if "title" not in self.configuration:
            self.configuration["title"] = "Webviz - Powered by Dash"

        if "pages" not in self.configuration and "layout" not in self.configuration:
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                "The configuration file does not have "
                "information regarding which pages to create."
                f"{terminal_colors.END}"
            )

        if "pages" in self.configuration and not isinstance(
            self.configuration["pages"], list
        ):
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                "The configuration input belonging to the "
                "`pages` keyword should be a list."
                f"{terminal_colors.END}"
            )

        if "pages" in self.configuration:
            warnings.warn(
                "The configuration keyword `pages` is going to be deprecated. "
                "Consider using the new `layout` keyword instead.",
                PendingDeprecationWarning,
            )

        if "layout" in self.configuration and not isinstance(
            self.configuration["layout"], list
        ):
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                "The configuration input belonging to the "
                "`layout` keyword should be a list."
                f"{terminal_colors.END}"
            )

        if "pageContents" not in self.configuration:
            self.configuration["pageContents"] = []

        self._parse_navigation()

    @property
    def configuration(self) -> dict:
        return self._configuration

    @property
    def shared_settings(self) -> dict:
        return self._shared_settings

    @property
    def assets(self) -> set:
        return self._assets

    @property
    def plugin_metadata(self) -> Dict[str, dict]:
        """Returns a dictionary of plugin metadata, and only for
        plugins included in the configuration file.
        """
        return self._plugin_metadata

    def _recursively_parse_navigation_item(self, items: dict, level: int) -> list:
        navigation_items: list = []
        for item_number, item in enumerate(items):
            if "section" in item:
                if level > 0:
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "Sections can only be defined on the first level"
                        f"{terminal_colors.END}"
                    )
                navigation_items.append(
                    {
                        "type": "section",
                        "title": item["section"],
                        "icon": item["icon"] if "icon" in item.keys() else None,
                        "content": self._recursively_parse_navigation_item(
                            item["content"], level + 1
                        )
                        if "content" in item.keys()
                        else [],
                    }
                )
            elif "group" in item:
                navigation_items.append(
                    {
                        "type": "group",
                        "title": item["group"],
                        "icon": item["icon"] if "icon" in item.keys() else None,
                        "content": self._recursively_parse_navigation_item(
                            item["content"], level + 1
                        )
                        if "content" in item.keys()
                        else [],
                    }
                )
            elif "page" in item or "title" in item:

                page_title = item["page"] if "page" in item else item["title"]
                if "id" not in item:
                    item["id"] = self._generate_page_id(page_title)
                elif item["id"] in self._page_ids:
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "You have more than one page "
                        "with the same `id`."
                        f"{terminal_colors.END}"
                    )

                self._page_ids.append(item["id"])

                if "content" not in item:
                    item["content"] = []
                elif not isinstance(item["content"], list):
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "The content of page number "
                        f"{item_number + 1} should be a list."
                        f"{terminal_colors.END}"
                    )

                self.configuration["pageContents"].append(item)

                navigation_items.append(
                    {
                        "type": "page",
                        "title": page_title,
                        "href": "/" + item["id"],
                        "icon": item["icon"] if "icon" in item.keys() else None,
                    }
                )

                plugins = [e for e in item["content"] if isinstance(e, dict)]
                for plugin in plugins:
                    plugin_name = next(iter(plugin))
                    plugin_variables = next(iter(plugin.values()))
                    kwargs = {} if plugin_variables is None else {**plugin_variables}

                    if plugin_name not in ConfigParser.STANDARD_PLUGINS:
                        raise ParserError(
                            f"{terminal_colors.RED}{terminal_colors.BOLD}"
                            "You have included a plugin with "
                            f"name `{plugin_name}` in your "
                            "configuration file. This is not a "
                            "standard plugin."
                            f"{terminal_colors.END}"
                        )

                    plugin["_call_signature"] = _call_signature(
                        plugin_name,
                        kwargs,
                        self._config_folder,
                    )

                    self._assets.update(
                        getattr(webviz_config.plugins, plugin_name).ASSETS
                    )
                    self._plugin_metadata[
                        plugin_name
                    ] = webviz_config.plugins.PLUGIN_METADATA[plugin_name]
        return navigation_items

    def _parse_navigation(self) -> None:
        # pylint: disable=too-many-branches
        """Returns a list of navigation items"""

        if "layout" in self.configuration:
            self.configuration[
                "navigation_items"
            ] = self._recursively_parse_navigation_item(self.configuration["layout"], 0)
        elif "pages" in self.configuration:
            self.configuration[
                "navigation_items"
            ] = self._recursively_parse_navigation_item(self.configuration["pages"], 0)

        options_found = False
        if "options" in self.configuration:
            if "menu" in self.configuration["options"]:
                options_found = True

                if "bar_position" not in self.configuration["options"]["menu"]:
                    self.configuration["options"]["menu"]["bar_position"] = "left"
                elif self.configuration["options"]["menu"]["bar_position"] not in [
                    "left",
                    "top",
                    "right",
                    "bottom",
                ]:
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "Invalid option for options > menu > bar_position: "
                        f"{self.configuration['options']['menu']['bar_position']}. "
                        "Please select one of the following options: left, top, right, bottom."
                        f"{terminal_colors.END}"
                    )

                if "drawer_position" not in self.configuration["options"]["menu"]:
                    self.configuration["options"]["menu"]["drawer_position"] = "left"
                elif self.configuration["options"]["menu"]["drawer_position"] not in [
                    "left",
                    "right",
                ]:
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "Invalid option for options > menu > drawer_position: "
                        f"{self.configuration['options']['menu']['drawer_position']}. "
                        "Please select one of the following options: left, right."
                        f"{terminal_colors.END}"
                    )

                if "initially_pinned" not in self.configuration["options"]["menu"]:
                    self.configuration["options"]["menu"]["initially_pinned"] = False
                elif not isinstance(
                    self.configuration["options"]["menu"]["initially_pinned"], bool
                ):
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "Invalid option for options > menu > initially_pinned: "
                        f"{self.configuration['options']['menu']['initially_pinned']}. "
                        "Please select a boolean value: True, False"
                        f"{terminal_colors.END}"
                    )

                if "initially_collapsed" not in self.configuration["options"]["menu"]:
                    self.configuration["options"]["menu"]["initially_collapsed"] = False
                elif not isinstance(
                    self.configuration["options"]["menu"]["initially_collapsed"], bool
                ):
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "Invalid option for options > menu > initially_collapsed: "
                        f"{self.configuration['options']['menu']['initially_collapsed']}. "
                        "Please select a boolean value: True, False"
                        f"{terminal_colors.END}"
                    )

                if "show_logo" not in self.configuration["options"]["menu"]:
                    self.configuration["options"]["menu"]["show_logo"] = True
                elif not isinstance(
                    self.configuration["options"]["menu"]["show_logo"], bool
                ):
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "Invalid option for options > menu > show_logo: "
                        f"{self.configuration['options']['menu']['show_logo']}. "
                        "Please select a boolean value: True, False"
                        f"{terminal_colors.END}"
                    )

        if not options_found:
            if "options" not in self.configuration:
                self.configuration["options"] = {}

            self.configuration["options"]["menu"] = {
                "bar_position": "left",
                "drawer_position": "left",
                "initially_pinned": False,
                "initially_collapsed": False,
                "show_logo": True,
            }

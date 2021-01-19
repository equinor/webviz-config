import re
import sys
import pathlib
import inspect
import typing

import yaml

from . import plugin_registry
from .utils import terminal_colors

SPECIAL_ARGS = ["self", "app", "webviz_settings", "_plugin_creation_spec"]


class PluginCreationSpec:
    """Contains spec for creating an instance of a webviz plugin"""

    def __init__(
        self, plugin_name: str, init_arg_str: str, layout_call_signature_str: str
    ) -> None:
        self.plugin_name = plugin_name
        self.init_arg_str = init_arg_str
        self.layout_call_signature_str = layout_call_signature_str


def _call_signature(
    plugin_name: str,
    kwargs: dict,
    config_folder: pathlib.Path,
    contact_person: typing.Optional[dict] = None,
) -> PluginCreationSpec:
    # pylint: disable=too-many-branches,too-many-statements
    """Takes as input the name of a plugin together with user given arguments
    (originating from the configuration file). Returns a plugin creation spec that
    has sufficien information to instantiate the wanted plugin instance (with the
    given arguments).

    Raises ParserError in the following scenarios:
      * User is missing a required (i.e. no default value) __init__ argument
      * User provided an argument not existing in the class' __init__ function
      * User has given one of the protected arguments in SPECIAL_ARGS
      * If there is type mismatch between user given argument value, and type
        hint in __init__ signature (given that type hint exist)
    """
    argspec = inspect.getfullargspec(plugin_registry.plugin_class(plugin_name).__init__)

    if argspec.defaults is not None:
        required_args = argspec.args[: -len(argspec.defaults)]
    else:
        required_args = argspec.args

    for arg in required_args:
        if arg not in SPECIAL_ARGS and arg not in kwargs:
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                f"`{plugin_name}` requires the argument "
                f"`{arg}` in your configuration file."
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
                f"does not take an argument `{arg}`."
                f"{terminal_colors.END}"
            )

        if arg in argspec.annotations:
            expected_type = argspec.annotations[arg]

            if expected_type == pathlib.Path:
                kwargs[arg] = (config_folder / pathlib.Path(kwargs[arg])).resolve()
            elif expected_type == typing.List[pathlib.Path]:
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
                        f"`{argspec.annotations[arg].__name__}`."
                        f"{terminal_colors.END}"
                    )
            # Typechecking typing classes does not work in python 3.7
            except TypeError:
                pass

    special_args = ""
    if "app" in argspec.args:
        special_args += "app=app, "
    if "webviz_settings" in argspec.args:
        special_args += "webviz_settings=webviz_settings, "

    return PluginCreationSpec(
        plugin_name=f"{plugin_name}",
        init_arg_str=f"{special_args}**{kwargs}",
        layout_call_signature_str=f"plugin_layout(contact_person={contact_person})",
    )


class ParserError(Exception):
    pass


class ConfigParser:
    def __init__(self, yaml_file: pathlib.Path):

        ConfigParser.check_for_tabs_in_file(yaml_file)

        try:
            self._configuration = yaml.safe_load(yaml_file.read_text())
        except yaml.MarkedYAMLError as excep:
            extra_info = (
                f"There is something wrong in the configuration file {yaml_file}. "
            )

            if hasattr(excep, "problem_mark"):
                extra_info += (
                    "The typo is probably somewhere around "
                    f"line {excep.problem_mark.line + 1}."
                )

            raise type(excep)(
                f"{excep}. {terminal_colors.RED}{terminal_colors.BOLD}"
                f"{extra_info}{terminal_colors.END}"
            ).with_traceback(sys.exc_info()[2])

        self._config_folder = pathlib.Path(yaml_file).parent
        self._page_ids: typing.List[str] = []
        self._assets: set = set()
        # TODO(Sigurd) Seems to be unused
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
        # pylint: disable=too-many-branches,too-many-statements
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

        if "pages" not in self.configuration:
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                "The configuration file does not have "
                "information regarding which pages to create."
                f"{terminal_colors.END}"
            )

        if not isinstance(self.configuration["pages"], list):
            raise ParserError(
                f"{terminal_colors.RED}{terminal_colors.BOLD}"
                "The configuration input belonging to the "
                "`pages` keyword should be a list."
                f"{terminal_colors.END}"
            )

        for page_number, page in enumerate(self.configuration["pages"]):

            if "title" not in page:
                raise ParserError(
                    f"{terminal_colors.RED}{terminal_colors.BOLD}"
                    f"Page number {page_number + 1} does "
                    "not have the title specified."
                    f"{terminal_colors.END}"
                )

            if "id" not in page:
                page["id"] = self._generate_page_id(page["title"])
            elif page["id"] in self._page_ids:
                raise ParserError(
                    f"{terminal_colors.RED}{terminal_colors.BOLD}"
                    "You have more than one page "
                    "with the same `id`."
                    f"{terminal_colors.END}"
                )

            self._page_ids.append(page["id"])

            if "content" not in page:
                page["content"] = []
            elif not isinstance(page["content"], list):
                raise ParserError(
                    f"{terminal_colors.RED}{terminal_colors.BOLD}"
                    "The content of page number "
                    f"{page_number + 1} should be a list."
                    f"{terminal_colors.END}"
                )

            # Plugin invocations, not direct strings
            # plugin_invocations
            plugin_entries_on_page = [e for e in page["content"] if isinstance(e, dict)]

            for entry in plugin_entries_on_page:
                plugin_name = next(iter(entry))
                plugin_variables = next(iter(entry.values()))
                kwargs = {} if plugin_variables is None else {**plugin_variables}

                if not plugin_registry.has_plugin(plugin_name):
                    raise ParserError(
                        f"{terminal_colors.RED}{terminal_colors.BOLD}"
                        "You have included a plugin with "
                        f"name `{plugin_name}` in your "
                        "configuration file. This is not a "
                        "standard plugin."
                        f"{terminal_colors.END}"
                    )

                plugin_creation_spec: PluginCreationSpec = _call_signature(
                    plugin_name,
                    kwargs,
                    self._config_folder,
                )
                # Attach the necessary spec for creating plugin instance to the page contents entry
                entry["_plugin_creation_spec"] = plugin_creation_spec

                self.assets.update(plugin_registry.plugin_class(plugin_name).ASSETS)

    @property
    def configuration(self) -> dict:
        return self._configuration

    @property
    def shared_settings(self) -> dict:
        return self._shared_settings

    @property
    def assets(self) -> set:
        return self._assets

import copy
import inspect
import pathlib
from typing import Callable, List, Dict


class SharedSettingsSubscriptions:
    """The user can configure common settings, shared between different cointainers,
    under a key called `shared_settings` in the configuration file. Since it originates
    from a native yaml file, the content is dictionaries/strings/ints/floats/dates.

    Third-party plugin packages might want to check early if the `shared_settings`
    they use are reasonable, and/or do some transformations on them.
    """

    def __init__(self) -> None:
        self._subscriptions: List[Dict] = []

    def subscribe(self, key: str) -> Callable:
        """This is the decorator, which third-party plugin packages will use."""

        def register(function: Callable) -> Callable:
            self._subscriptions.append({"key": key, "function": function})
            return function

        return register

    def transformed_settings(
        self, shared_settings: Dict, config_folder: str, portable: bool
    ) -> Dict:
        """Called from the app template, which returns the `shared_settings`
        after all third-party package subscriptions have done their
        (optional) transfomrations.
        """
        shared_settings = copy.deepcopy(shared_settings)

        for subscription in self._subscriptions:
            key, function = subscription["key"], subscription["function"]
            shared_settings[key] = function(
                *[
                    pathlib.Path(config_folder)
                    if arg == "config_folder"
                    else portable
                    if arg == "portable"
                    else shared_settings.get(arg)
                    for arg in inspect.getfullargspec(function).args
                ]
            )

        return shared_settings


SHARED_SETTINGS_SUBSCRIPTIONS = SharedSettingsSubscriptions()

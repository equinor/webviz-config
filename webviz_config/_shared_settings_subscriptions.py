import copy
import inspect
import pathlib


class SharedSettingsSubscriptions:
    """The user can configure common settings, shared between different cointainers,
    under a key called `shared_settings` in the configuration file. Since it originates
    from a native yaml file, the content is dictionaries/strings/ints/floats/dates.

    Third-party container packages might want to check early if the `shared_settings`
    they use are reasonable, and/or do some transformations on them.
    """

    def __init__(self):
        self._subscriptions = []

    def subscribe(self, key):
        """This is the decorator, which third-party container packages will use.
        """

        def register(function):
            self._subscriptions.append({"key": key, "function": function})
            return function

        return register

    def transformed_settings(self, shared_settings, config_folder):
        """Called from the app template, which returns the `shared_settings`
        after all third-party package subscriptions have done their
        (optional) transfomrations.
        """
        shared_settings = copy.deepcopy(shared_settings)

        for subscription in self._subscriptions:
            key, function = subscription["key"], subscription["function"]
            requires_config_folder = len(inspect.getfullargspec(function).args) > 1
            shared_settings[key] = (
                function(shared_settings.get(key), pathlib.Path(config_folder))
                if requires_config_folder
                else function(shared_settings.get(key))
            )

        return shared_settings


SHARED_SETTINGS_SUBSCRIPTIONS = SharedSettingsSubscriptions()

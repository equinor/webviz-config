from typing import Any, List, Optional, Dict, Callable, Union
from dataclasses import dataclass


@dataclass(frozen=True)
class DeprecatedPlugin:
    class_reference: Any
    short_message: str
    long_message: str


@dataclass(frozen=True)
class DeprecatedArgument:
    method_reference: Any
    method_name: str
    argument_name: str
    argument_value: str
    short_message: str
    long_message: str


@dataclass(frozen=True)
class DeprecatedArgumentCheck:
    method_reference: Any
    method_name: str
    argument_names: List[str]
    callback: Callable
    callback_code: str


class DeprecationStore:
    def __init__(self) -> None:
        self.stored_plugin_deprecations: Dict[Any, DeprecatedPlugin] = {}
        self.stored_plugin_argument_deprecations: List[
            Union[DeprecatedArgument, DeprecatedArgumentCheck]
        ] = []

    def register_deprecated_plugin(self, deprecated_plugin: DeprecatedPlugin) -> None:
        """This function is automatically called by the decorator
        @deprecated_plugin, registering the plugin it decorates.
        """
        self.stored_plugin_deprecations[
            deprecated_plugin.class_reference
        ] = deprecated_plugin

    def register_deprecated_plugin_argument(
        self,
        deprecated_plugin_argument: Union[DeprecatedArgument, DeprecatedArgumentCheck],
    ) -> None:
        """This function is automatically called by the decorator
        @deprecated_plugin_arguments, registering the __init__ function it decorates.
        """
        self.stored_plugin_argument_deprecations.append(deprecated_plugin_argument)

    def get_stored_plugin_deprecation(self, plugin: Any) -> Optional[DeprecatedPlugin]:
        return self.stored_plugin_deprecations.get(plugin)

    def get_stored_plugin_argument_deprecations(
        self, method: Callable
    ) -> List[Union[DeprecatedArgument, DeprecatedArgumentCheck]]:
        return [
            stored
            for stored in self.stored_plugin_argument_deprecations
            if stored.method_reference == method
        ]


DEPRECATION_STORE = DeprecationStore()

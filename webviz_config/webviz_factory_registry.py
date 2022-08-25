from typing import Any, Dict, Optional, Type, TypeVar
import warnings

from .webviz_factory import WebvizFactory
from .webviz_instance_info import WebvizInstanceInfo, WEBVIZ_INSTANCE_INFO

T = TypeVar("T", bound=WebvizFactory)


class WebvizFactoryRegistry:
    """Global registry for factories that allows the actual factory instances
    to be shared between plugins. Also facilitates storage of optional factory
    settings that are read from the YAML config file for later consumption when
    an actual factory gets created and added to the registry.
    The registry is exposed globally through WEBVIZ_FACTORY_REGISTRY below.
    This is also the reason for the two-stage initialization approach. Note that
    the registry instance is useless until the initialize() method has been called.

    Note that this functionality is provisional/experimental, and will not necessarily
    see a deprecation phase and "may deviate from the usual version semantics."
    """

    def __init__(self) -> None:
        self._is_initialized: bool = False
        self._factory_settings_dict: Dict[str, Any] = {}
        self._factories: Dict[Type, WebvizFactory] = {}

    def initialize(
        self,
        factory_settings_dict: Optional[Dict[str, Any]],
    ) -> None:
        """Does the actual initialization of the object instance.
        This function will be called as part of the webviz_app.py / jinja2 template.
        """
        if self._is_initialized:
            raise RuntimeError("Registry already initialized")

        if factory_settings_dict:
            if not isinstance(factory_settings_dict, dict):
                raise TypeError("factory_settings_dict must be of type dict")
            self._factory_settings_dict = factory_settings_dict

        self._is_initialized = True

    def set_factory(self, factory_class: Type[T], factory_obj: T) -> None:
        if not self._is_initialized:
            raise RuntimeError("Illegal access, factory registry is not initialized")

        if not isinstance(factory_obj, factory_class):
            raise TypeError("The type of the factory does not match factory_class")

        self._factories[factory_class] = factory_obj

    def get_factory(self, factory_class: Type[T]) -> Optional[T]:
        if not self._is_initialized:
            raise RuntimeError("Illegal access, factory registry is not initialized")

        if not factory_class in self._factories:
            return None

        factory_obj = self._factories[factory_class]
        if not isinstance(factory_obj, factory_class):
            raise TypeError("The stored factory object has wrong type")

        return factory_obj

    def cleanup_resources_after_plugin_init(self) -> None:
        if not self._is_initialized:
            raise RuntimeError("Illegal access, factory registry is not initialized")

        for factory in self._factories.values():
            factory.cleanup_resources_after_plugin_init()

    @property
    def all_factory_settings(self) -> Dict[str, Any]:
        if not self._is_initialized:
            raise RuntimeError("Illegal access, factory registry is not initialized")

        return self._factory_settings_dict

    @property
    def app_instance_info(self) -> WebvizInstanceInfo:
        warnings.warn(
            "Accessing WebvizInstanceInfo through WebvizFactoryRegistry has been deprecated, "
            "please use global WEBVIZ_INSTANCE_INFO instead",
            DeprecationWarning,
        )

        return WEBVIZ_INSTANCE_INFO


WEBVIZ_FACTORY_REGISTRY = WebvizFactoryRegistry()

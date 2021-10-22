from typing import Dict, Union, Callable, Tuple, cast, Optional, List, Type
import inspect

from ._plugin_abc import WebvizPluginABC
from . import _deprecation_store as _ds


def deprecated_plugin(
    deprecation_info: str = "",
) -> Callable[[Type[WebvizPluginABC]], Type[WebvizPluginABC]]:
    def wrapper(
        original_plugin: Type[WebvizPluginABC],
    ) -> Type[WebvizPluginABC]:

        _ds.DEPRECATION_STORE.register_deprecated_plugin(
            _ds.DeprecatedPlugin(
                original_plugin,
                f"Plugin '{original_plugin.__name__}' has been deprecated.",
                deprecation_info,
            )
        )

        return original_plugin

    return wrapper


def deprecated_plugin_arguments(
    check: Union[Dict[str, str], Callable[..., Optional[Tuple[str, str]]]]
) -> Callable:
    def decorator(original_init_method: Callable) -> Callable:
        original_method_args = inspect.getfullargspec(original_init_method).args

        if callable(check):
            check_args = inspect.getfullargspec(check).args
            verified_args: List[str] = []
            for check_arg in check_args:
                for original_arg in original_method_args:
                    if check_arg == original_arg:
                        verified_args.append(check_arg)

            _ds.DEPRECATION_STORE.register_deprecated_plugin_argument(
                _ds.DeprecatedArgumentCheck(
                    original_init_method,
                    original_init_method.__name__,
                    verified_args,
                    check,
                    inspect.getsource(check),
                )
            )

        elif isinstance(check, dict):
            for original_arg in original_method_args:
                if original_arg in check.keys():
                    short_message = cast(Tuple[str, str], check[original_arg])[0]
                    long_message = cast(Tuple[str, str], check[original_arg])[1]
                    _ds.DEPRECATION_STORE.register_deprecated_plugin_argument(
                        _ds.DeprecatedArgument(
                            original_init_method,
                            original_init_method.__name__,
                            original_arg,
                            "",
                            short_message,
                            long_message,
                        )
                    )
        return original_init_method

    return decorator

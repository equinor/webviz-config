import types
import typing
import inspect

from .._plugin_abc import WebvizPluginABC


def _get_webviz_plugins(module: types.ModuleType) -> list:
    """Returns a list of all Webviz plugins
    in the module given as input.
    """

    def _is_webviz_plugin(obj: typing.Any) -> bool:
        return (
            inspect.isclass(obj)
            and issubclass(obj, WebvizPluginABC)
            and obj is not WebvizPluginABC
        )

    return inspect.getmembers(module, _is_webviz_plugin)

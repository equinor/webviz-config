from typing import Any, Generator

# pylint: disable=too-few-public-methods
class MissingWebvizTesting:
    def __init__(self, **kwargs: Any) -> None:
        raise RuntimeError(
            "webviz_config[tests] was not installed. "
            "Please install to use the webviz testing fixtures."
        )


try:
    from ._composite import WebvizComposite

except ImportError:
    WebvizComposite = MissingWebvizTesting  # type: ignore

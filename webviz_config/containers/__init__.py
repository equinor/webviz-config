import warnings

from ..plugins import *

warnings.simplefilter("default", DeprecationWarning)

warnings.warn(
    (
        "The submodule 'webviz_config.containers' is deprecated. You "
        "should change to 'webviz_config.plugins'. This warning will eventually "
        "turn into an error in a future release of webviz-config."
    ),
    DeprecationWarning,
)

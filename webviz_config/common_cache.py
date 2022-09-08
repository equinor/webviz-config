import warnings

import flask_caching


class Cache(flask_caching.Cache):
    def __init__(
        self,
    ) -> None:

        super().__init__(config={"CACHE_TYPE": "simple", "DEFAULT_CACHE_TIMEOUT": 3600})

    @property
    def TIMEOUT(self) -> int:  # pylint: disable=invalid-name
        warnings.warn(
            "Default cache timeout is now initialized directly, and the TIMEOUT "
            "attribute is therefore deprecated, and will be removed. The timeout "
            "argument can still be used as input to @CACHE.memoize() with an input "
            "if you want to overwride the 3600 (seconds) webviz default.",
            DeprecationWarning,
        )
        return 3600


CACHE = Cache()

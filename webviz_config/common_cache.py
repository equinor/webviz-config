import flask_caching


CACHE = flask_caching.Cache(
    config={"CACHE_TYPE": "simple", "DEFAULT_CACHE_TIMEOUT": 3600}
)

import flask_caching


CACHE = flask_caching.Cache(config={"CACHE_TYPE": "simple"})
CACHE.TIMEOUT = 3600

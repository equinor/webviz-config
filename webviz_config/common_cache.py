import flask_caching


CACHE = flask_caching.Cache(
    config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "./flaskcaching"}
)
CACHE.TIMEOUT = 3600

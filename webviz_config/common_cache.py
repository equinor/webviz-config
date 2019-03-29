import flask_caching


cache = flask_caching.Cache(config={'CACHE_TYPE': 'simple'})
cache.TIMEOUT = 60

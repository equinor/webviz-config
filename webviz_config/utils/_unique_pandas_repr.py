import hashlib
from typing import Union

import pandas as pd


def _hash_pandas_object(
    obj: Union[pd.DataFrame, pd.Series], columns_exist: bool
) -> str:

    content_as_bytes = obj.index.values.tobytes() + obj.values.tobytes()
    if columns_exist:
        content_as_bytes += obj.columns.values.tobytes()

    return hashlib.sha256(content_as_bytes).hexdigest()


def patch_unique_pandas_repr() -> None:
    """flask-caching package uses repr() on input arguments to create
    unique hashes of function arguments, in order to cache expensive function calls.

    This works as long as repr() on individual input arguments behaves such that
    repr() gives a unique and deterministic representation string, for instances
    which intuitively represent the same "data"/values.

    For pandas.DataFrames and pandas.Series, which are commonly used by plugin authors,
    this is not entirely the case by default. Their repr() depends on pandas print
    settings (how e.g. DataFrames should be printed to terminal). In addition,
    their __str__ and __repr__ functions are identical.

    Since there is a large risk for plugin authors forgetting that input arguments
    need a unique repr (combined with pandas objects being commonly used), we either
    need to special case Pandas objects in upstream flask-caching, or
    make pandas __repr__ functions unique + deterministic. This function does the
    latter by monkey-patching pandas.DataFrame.__repr__ and pandas.Series.__repr__.

    NOTE: This function is only a short-term change. Long-term we will help
    plugin authors not use pandas objects in cached function calls using the
    planned Webviz pytest fixture.
    """

    pd.DataFrame.__str__ = pd.DataFrame.__repr__
    pd.DataFrame.__repr__ = (
        lambda self: f"<pandas.DataFrame {_hash_pandas_object(self, True)}>"
    )

    pd.Series.__str__ = pd.Series.__repr__
    pd.Series.__repr__ = (
        lambda self: f"<pandas.Series {self.name} {_hash_pandas_object(self, False)}>"
    )

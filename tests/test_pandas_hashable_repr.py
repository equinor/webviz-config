import sys

import pytest
import pandas as pd

import webviz_config.webviz_store  # pylint: disable=unused import


@pytest.mark.parametrize(
    "input_object, hash",
    [
        (
            pd.DataFrame([1.0, 2.0, 3.0], dtype=float),
            "7934426400b4769c327486968f836f9c2c7f798c47b65bf3ed6d1babc90134ff",
        ),
        (
            pd.DataFrame([1.0, 2.0, 3.0 + sys.float_info.epsilon], dtype=float),
            "7934426400b4769c327486968f836f9c2c7f798c47b65bf3ed6d1babc90134ff",
        ),
        (
            pd.DataFrame([1, 2, 3], dtype=int),
            "9b1675ee7524ed8840aedbfd5a224a70d23dae07c6be0fcaf5ad596065072e92",
        ),
        (
            pd.DataFrame([1.0, 2.0, 3.0], columns=["A"]),
            "203afebaf24dbeb72565276f68d0085e5c6f38190b1003f1b900f992fee34c49",
        ),
        (
            pd.Series([1, 2, 3], dtype=int),
            "a96335a76cf73d8722fa035b7f360acfb5d4b76068570e71fb166dfb9beb13d7",
        ),
        (
            pd.Series([1, 2, 3], dtype=int, name="Some name"),
            "3b2fe2c10b8164593b891877480f9f6fb3ea96970f5e85ce9163eb11a674aaf0",
        ),        
    ],
)
def test_pandas_object_repr(input_object, hash):
    type_str = 'DataFrame' if isinstance(input_object, pd.DataFrame) else 'Series'

    assert repr(input_object) == f"<pandas.{type_str} webviz_config.webviz_storage repr {hash}>"

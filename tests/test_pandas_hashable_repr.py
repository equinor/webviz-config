import pytest
import pandas as pd

from webviz_config.utils.hashable_pandas_repr import hashable_pandas_repr

hashable_pandas_repr()

@pytest.mark.parametrize(
    "input_df, expected_repr",
    [
        (
            pd.DataFrame([1.0, 2.0, 3.0]),
            "<pandas.DataFrame 7934426400b4769c327486968f836f9c2c7f798c47b65bf3ed6d1babc90134ff>",
        ),
        (
            pd.DataFrame([1, 2, 3], dtype=int),
            "<pandas.DataFrame 9b1675ee7524ed8840aedbfd5a224a70d23dae07c6be0fcaf5ad596065072e92>",
        ),
        (
            pd.DataFrame([1.0, 2.0, 3.0], columns=["A"]),
            "<pandas.DataFrame 203afebaf24dbeb72565276f68d0085e5c6f38190b1003f1b900f992fee34c49>",
        ),
        (
            pd.Series([1, 2, 3], dtype=int),
            "<pandas.Series None 5dc0e486aeb50a730b513d618420aacab5a8f026e4846209a4f3e3799ad6a044>",
        ),
    ],
)
def test_pandas_object_repr(input_object, expected_repr):
    assert repr(input_object) == expected_repr


print(repr(pd.Series([1, 2, 3], dtype=int)))

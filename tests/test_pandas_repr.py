import pytest
import pandas as pd

from webviz_config.utils._unique_pandas_repr import patch_unique_pandas_repr

patch_unique_pandas_repr()


@pytest.mark.parametrize(
    "input_object, expected_repr",
    [
        (
            pd.DataFrame([1.0, 2.0, 3.0]),
            "<pandas.DataFrame 2cf0f06b70bcb120b23e010f2bfb4a2d777c2bd5db71e922e6eb48e891a16331>",
        ),
        (
            pd.DataFrame([1, 2, 3], dtype=int),
            "<pandas.DataFrame 42ec3328931d3566010f1d046910187cc24b221174c8e5db68d9b5d6e80edc84>",
        ),
        (
            pd.DataFrame([1.0, 2.0, 3.0], columns=["A"]),
            "<pandas.DataFrame f332456eb7677163bdfab48e9e46bac02cfa56c78c7db3d3bbdd30c6abeb9bfd>",
        ),
        (
            pd.Series([1, 2, 3], dtype=int),
            "<pandas.Series None c12eeadb2b9b01ca4288a92e54d6df638928b7501181319f6d534632bf93fc96>",
        ),
    ],
)
def test_pandas_object_repr(input_object, expected_repr):
    assert repr(input_object) == expected_repr

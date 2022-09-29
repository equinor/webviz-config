from typing import List

import pandas as pd

from .. import WebvizPluginABC
from ..webviz_store import webvizstore
from ..common_cache import CACHE


class ExamplePortable(WebvizPluginABC):
    def __init__(self, some_number: int):
        super().__init__()

        self.some_number = some_number
        self.some_string = "a"

    def add_webvizstore(self) -> List[tuple]:
        return [
            (
                input_data_function,
                [{"some_string": self.some_string, "some_number": self.some_number}],
            )
        ]

    @property
    def layout(self) -> str:
        return str(input_data_function(self.some_string, some_number=self.some_number))


@CACHE.memoize()
@webvizstore
def input_data_function(
    some_string: str, some_number: int, some_bool: bool = True
) -> pd.DataFrame:
    print("This time I'm actually doing the calculation...")
    return pd.DataFrame(
        data={
            "col1": [some_number, some_number * 2],
            "col2": [some_number * 3, some_number * 4],
            "col3": [some_string, some_string + "b"],
            "col4": [some_bool, not some_bool],
        }
    )

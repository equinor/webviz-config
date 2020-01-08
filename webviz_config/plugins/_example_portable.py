import pandas as pd

from .. import WebvizPluginABC
from ..webviz_store import webvizstore
from ..common_cache import CACHE


class ExamplePortable(WebvizPluginABC):
    def __init__(self, some_number: int):
        super().__init__()

        self.some_number = some_number

    def add_webvizstore(self):
        return [(input_data_function, [{"some_number": self.some_number}])]

    @property
    def layout(self):
        return str(input_data_function(self.some_number))


@CACHE.memoize(timeout=CACHE.TIMEOUT)
@webvizstore
def input_data_function(some_number) -> pd.DataFrame:
    print("This time I'm actually doing the calculation...")
    return pd.DataFrame(
        data={
            "col1": [some_number, some_number * 2],
            "col2": [some_number * 3, some_number * 4],
        }
    )

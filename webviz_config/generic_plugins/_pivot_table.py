from pathlib import Path
from typing import List

import pandas as pd
import dash_pivottable

from .. import WebvizPluginABC
from ..webviz_store import webvizstore
from ..common_cache import CACHE


class PivotTable(WebvizPluginABC):
    """Adds a pivot table to the webviz instance, using tabular data from a \
        provided csv file.

---

* **`csv_file`:** Path to the csv file containing the tabular data. Either absolute \
                  path or relative to the configuration file.
* **`options`:** Additional options for the plot. See [dash-pivottable documentation]\
    (https://github.com/plotly/dash-pivottable#references) for all possible options.
"""

    def __init__(self, csv_file: Path, options: dict = None):

        super().__init__()

        self.csv_file = csv_file
        self.options = options if options is not None else {}

    def add_webvizstore(self) -> List[tuple]:
        return [(get_data, [{"csv_file": self.csv_file}])]

    @property
    def layout(self) -> dash_pivottable.PivotTable:
        return generate_table(get_data(self.csv_file), **self.options)


def generate_table(dframe: pd.DataFrame, **options: str) -> dash_pivottable.PivotTable:
    return dash_pivottable.PivotTable(
        data=[dframe.columns.to_list()] + dframe.values.tolist(), **options
    )


@CACHE.memoize(timeout=CACHE.TIMEOUT)
@webvizstore
def get_data(csv_file: Path) -> pd.DataFrame:
    return pd.read_csv(csv_file)

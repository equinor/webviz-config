from pathlib import Path
from typing import List

import pandas as pd
from dash import dash_table

from .. import WebvizPluginABC
from ..webviz_store import webvizstore
from ..common_cache import CACHE


class DataTable(WebvizPluginABC):
    """Adds a table to the webviz instance, using tabular data from a provided csv file.
If feature is requested, the data could also come from a database.

---

* **`csv_file`:** Path to the csv file containing the tabular data. Either absolute \
              path or relative to the configuration file.
* **`sorting`:** If `True`, the table can be sorted interactively based \
             on data in the individual columns.
* **`filtering`:** If `True`, the table can be filtered based on values in the \
               individual columns.
* **`pagination`:** If `True`, only a subset of the table is displayed at once. \
                Different subsets can be viewed from 'previous/next' buttons
"""

    def __init__(
        self,
        csv_file: Path,
        sorting: bool = True,
        filtering: bool = True,
        pagination: bool = True,
    ):

        super().__init__()

        self.csv_file = csv_file
        self.df = get_data(self.csv_file)
        self.sorting = sorting
        self.filtering = filtering
        self.pagination = pagination

    def add_webvizstore(self) -> List[tuple]:
        return [(get_data, [{"csv_file": self.csv_file}])]

    @property
    def layout(self) -> dash_table.DataTable:
        return dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in self.df.columns],
            data=self.df.to_dict(  # PyCQA/pylint#4577 # pylint: disable=no-member
                "records"
            ),
            sort_action="native" if self.sorting else "none",
            filter_action="native" if self.filtering else "none",
            page_action="native" if self.pagination else "none",
        )


@CACHE.memoize(timeout=CACHE.TIMEOUT)
@webvizstore
def get_data(csv_file: Path) -> pd.DataFrame:
    return pd.read_csv(csv_file)

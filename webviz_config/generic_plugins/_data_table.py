import base64
from pathlib import Path
from typing import List, Optional

import pandas as pd
from dash import dash_table, Dash

from .. import WebvizPluginABC, EncodedFile
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
        app: Dash,
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

        self.set_callbacks(app)

    def add_webvizstore(self) -> List[tuple]:
        return [(get_data, [{"csv_file": self.csv_file}])]

    @property
    def layout(self) -> dash_table.DataTable:
        return dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in self.df.columns],
            data=self.df.to_dict("records"),
            sort_action="native" if self.sorting else "none",
            filter_action="native" if self.filtering else "none",
            page_action="native" if self.pagination else "none",
        )

    def set_callbacks(self, app: Dash) -> None:
        @app.callback(self.plugin_data_output, self.plugin_data_requested)
        def _user_download_data(data_requested: Optional[int]) -> Optional[EncodedFile]:
            return (
                {
                    "filename": "data-table.csv",
                    "content": base64.b64encode(
                        get_data(self.csv_file).to_csv(index=False).encode()
                    ).decode("ascii"),
                    "mime_type": "text/csv",
                }
                if data_requested
                else None
            )


@CACHE.memoize()
@webvizstore
def get_data(csv_file: Path) -> pd.DataFrame:
    return pd.read_csv(csv_file)

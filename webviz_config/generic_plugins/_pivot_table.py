import base64
from pathlib import Path
from typing import List, Optional

import pandas as pd
from dash import Dash
import dash_pivottable

from .. import WebvizPluginABC, EncodedFile
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

    def __init__(self, app: Dash, csv_file: Path, options: dict = None):

        super().__init__()

        self.csv_file = csv_file
        self.options = options if options is not None else {}

        self.set_callbacks(app)

    def add_webvizstore(self) -> List[tuple]:
        return [(get_data, [{"csv_file": self.csv_file}])]

    @property
    def layout(self) -> dash_pivottable.PivotTable:
        return generate_table(get_data(self.csv_file), **self.options)

    def set_callbacks(self, app: Dash) -> None:
        @app.callback(self.plugin_data_output, self.plugin_data_requested)
        def _user_download_data(data_requested: Optional[int]) -> Optional[EncodedFile]:
            return (
                {
                    "filename": "pivot-table.csv",
                    "content": base64.b64encode(
                        get_data(self.csv_file).to_csv(index=False).encode()
                    ).decode("ascii"),
                    "mime_type": "text/csv",
                }
                if data_requested
                else None
            )


def generate_table(dframe: pd.DataFrame, **options: str) -> dash_pivottable.PivotTable:
    return dash_pivottable.PivotTable(
        data=[dframe.columns.to_list()] + dframe.values.tolist(), **options
    )


@CACHE.memoize()
@webvizstore
def get_data(csv_file: Path) -> pd.DataFrame:
    return pd.read_csv(csv_file)

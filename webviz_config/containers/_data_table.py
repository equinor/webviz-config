from uuid import uuid4
from pathlib import Path
import pandas as pd
import dash_table
from ..webviz_store import webvizstore
from ..common_cache import cache


class DataTable:
    '''### Data table

This container adds a table to the webviz instance, using tabular data from
a provided csv file. If feature is requested, the data could also come from
a database.

* `csv_file`: Path to the csv file containing the tabular data. Either absolute
              path or relative to the configuration file.
* `sorting`: If `True`, the table can be sorted interactively based
             on data in the individual columns.
* `filtering`: If `True`, the table can be filtered based on values in the
               individual columns.
'''

    def __init__(self, csv_file: Path, sorting: bool = True,
                 filtering: bool = False):

        self.csv_file = csv_file
        self.df = get_data(self.csv_file)
        self.sorting = sorting
        self.filtering = filtering
        self.data_table_id = 'data-table-{}'.format(uuid4())

    def add_webvizstore(self):
        return [(get_data, [{'csv_file': self.csv_file}])]

    @property
    def layout(self):
        return dash_table.DataTable(
                 id=self.data_table_id,
                 columns=[{'name': i, 'id': i} for i in self.df.columns],
                 data=self.df.to_dict('records'),
                 sorting=self.sorting,
                 filtering=self.filtering
                        )


@cache.memoize(timeout=cache.TIMEOUT)
@webvizstore
def get_data(csv_file) -> pd.DataFrame:
    return pd.read_csv(csv_file)

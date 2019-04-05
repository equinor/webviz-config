'''### _Basic containers_

These are the basic Webviz configuration containers, distributed through
the utility itself.
'''

import pkg_resources

from ._example_container import ExampleContainer
from ._example_assets import ExampleAssets
from ._example_portable import ExamplePortable
from ._banner_image import BannerImage
from ._data_table import DataTable
from ._syntax_highlighter import SyntaxHighlighter
from ._table_plotter import TablePlotter

__all__ = ['ExampleContainer',
           'ExampleAssets',
           'ExamplePortable',
           'BannerImage',
           'DataTable',
           'SyntaxHighlighter',
           'TablePlotter']

for entry_point in pkg_resources.iter_entry_points('webviz_config_containers'):
    globals()[entry_point.name] = entry_point.load()

    __all__.append(entry_point.name)

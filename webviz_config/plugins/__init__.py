"""These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

import pkg_resources

from ._example_plugin import ExamplePlugin
from ._example_data_download import ExampleDataDownload
from ._example_assets import ExampleAssets
from ._example_portable import ExamplePortable
from ._example_tour import ExampleTour
from ._banner_image import BannerImage
from ._data_table import DataTable
from ._syntax_highlighter import SyntaxHighlighter
from ._table_plotter import TablePlotter
from ._embed_pdf import EmbedPdf
from ._markdown import Markdown

__all__ = [
    "ExamplePlugin",
    "ExampleAssets",
    "ExamplePortable",
    "ExampleTour",
    "BannerImage",
    "DataTable",
    "SyntaxHighlighter",
    "TablePlotter",
    "EmbedPdf",
    "Markdown",
]

for entry_point in pkg_resources.iter_entry_points("webviz_config_plugins"):
    globals()[entry_point.name] = entry_point.load()
    __all__.append(entry_point.name)

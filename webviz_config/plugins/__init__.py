"""### _Basic plugins_

These are the basic Webviz configuration plugins, distributed through
the utility itself.
"""

import warnings

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

warnings.simplefilter("default", DeprecationWarning)

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

for entry_point in pkg_resources.iter_entry_points("webviz_config_containers"):
    globals()[entry_point.name] = entry_point.load()
    __all__.append(entry_point.name)

    warnings.warn(
        (
            "The setup.py entry point name 'webviz_config_containers' is deprecated. "
            "You should change to 'webviz_config_plugins'. This warning will "
            "eventually turn into an error in a future release of webviz-config."
        ),
        DeprecationWarning,
    )

for entry_point in pkg_resources.iter_entry_points("webviz_config_plugins"):
    globals()[entry_point.name] = entry_point.load()
    __all__.append(entry_point.name)

from pathlib import Path

from dash import html

from .. import WebvizPluginABC
from ..webviz_assets import WEBVIZ_ASSETS


class EmbedPdf(WebvizPluginABC):
    """Embeds a given PDF file into the page.

!> Webviz does not scan your PDF for malicious code. Make sure it comes from a trusted source.
---

* **`pdf_file`:** Path to the PDF file to include. Either absolute path or \
  relative to the configuration file.
* **`height`:** Height of the PDF object (in percent of viewport height).
* **`width`:** Width of the PDF object (in percent of available space).

"""

    def __init__(self, pdf_file: Path, height: int = 80, width: int = 100):

        super().__init__()

        self.pdf_url = WEBVIZ_ASSETS.add(pdf_file)
        self.height = height
        self.width = width

    @property
    def layout(self) -> html.Embed:

        style = {"height": f"{self.height}vh", "width": f"{self.width}%"}

        return html.Embed(src=self.pdf_url, style=style, type="application/pdf")

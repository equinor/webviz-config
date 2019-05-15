from pathlib import Path
import dash_dangerously_set_inner_html
from ..webviz_assets import webviz_assets


class EmbedPdf:
    '''### Embed PDF file

This container embeds a given PDF file into the page.

* `pdf_file`: Path to the PDF file to include. Either absolute path or
  relative to the configuration file.
* `height`: Height of the PDF object (in pixels).
'''

    def __init__(self, pdf_file: Path, height: int = 600):
        self.pdf_url = webviz_assets.add(pdf_file)
        self.height = height

    @property
    def layout(self):
        html = (f'<embed src="{self.pdf_url}" type="application/pdf" '
                f'width="100%" height="{self.height}px" />')

        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(html)

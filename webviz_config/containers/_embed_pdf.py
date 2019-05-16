from pathlib import Path
import dash_html_components as html
from ..webviz_assets import webviz_assets


class EmbedPdf:
    '''### Embed PDF file

This container embeds a given PDF file into the page.

* `pdf_file`: Path to the PDF file to include. Either absolute path or
  relative to the configuration file.
* `height`: Height of the PDF object (in percent of viewport height).
* `width`: Width of the PDF object (in percent of available space).

_Note_: Webviz does not scan your PDF for malicious code.
Make sure it comes from a trusted source.
'''

    def __init__(self, pdf_file: Path, height: int = 80, width: int = 100):
        self.pdf_url = webviz_assets.add(pdf_file)
        self.height = height
        self.width = width

    @property
    def layout(self):

        style = {
                 'height': f'{self.height}vh',
                 'width': f'{self.width}%'
                }

        return html.Embed(src=self.pdf_url,
                          style=style,
                          type='application/pdf')

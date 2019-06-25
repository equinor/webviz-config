from uuid import uuid4
from pathlib import Path
import dash_core_components as dcc
from . import WebvizContainer
from ..webviz_store import webvizstore


class SyntaxHighlighter(WebvizContainer):
    '''### Syntax highlighter

This container adds support for syntax highlighting of code. Language is
automatically detected.

* `filename`: Path to a file containing the code to highlight.
* `dark_theme`: If `True`, the code is shown with a dark theme. Default is
                `False` giving a light theme.
'''

    def __init__(self, filename: Path, dark_theme: bool = False):

        self.filename = filename
        self.config = {'theme': 'dark'} if dark_theme else {'theme': 'light'}

    def add_webvizstore(self):
        return [(get_path, [{'path': self.filename}])]

    @property
    def layout(self):
        return dcc.Markdown(f'```{get_path(self.filename).read_text()}```',
                            highlight_config=self.config)


@webvizstore
def get_path(path) -> Path:
    return path

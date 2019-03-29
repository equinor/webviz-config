from uuid import uuid4
from pathlib import Path
import dash_core_components as dcc
from ..webviz_store import webvizstore


class SyntaxHighlighter:
    '''### Syntax highlighter

This container adds support for syntax highlighting of code. Language is
automatically detected.

* `filename`: Path to a file containing the code to highlight.
* `show_line_numbers`: If `True`, show line numbers. Default is `False`.
* `start_number`: This only has effect if `show_line_numbers` is `True`. If
                  given, line numbers will start at this value. Default is `1`.
* `dark_theme`: If `True`, the code is shown with a dark theme. Default is
                `False` giving a light theme.
'''

    def __init__(self, filename: Path, show_line_numbers: bool = False,
                 start_number: int = 1, dark_theme: bool = False):

        self.filename = filename
        self.show_line_numbers = show_line_numbers
        self.start_number = start_number
        self.dark_theme = dark_theme

        self.syntax_highlighter_id = 'syntax-highlighter-{}'.format(uuid4())

        with get_path(self.filename).open() as fh:
            self.code = fh.read()

    def add_webvizstore(self):
        return [(get_path, [{'path': self.filename}])]

    @property
    def layout(self):
        return dcc.SyntaxHighlighter(
                 id=self.syntax_highlighter_id,
                 children=self.code,
                 showLineNumbers=self.show_line_numbers,
                 startingLineNumber=self.start_number,
                 theme='dark' if self.dark_theme else 'light'
                        )


@webvizstore
def get_path(path) -> Path:
    return path

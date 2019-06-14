from pathlib import Path
import bleach
import markdown
from markdown.util import etree
from markdown.extensions import Extension
from markdown.inlinepatterns import ImageInlineProcessor, IMAGE_LINK_RE
import dash_core_components as html
from . import WebvizContainer
from ..webviz_assets import webviz_assets
from ..webviz_store import webvizstore


class _WebvizMarkdownExtension(Extension):
    def __init__(self, base_path):
        self.base_path = base_path

        super(_WebvizMarkdownExtension, self).__init__()

    def extendMarkdown(self, md):
        md.inlinePatterns['image_link'] = \
            _MarkdownImageProcessor(IMAGE_LINK_RE, md, self.base_path)


class _MarkdownImageProcessor(ImageInlineProcessor):
    def __init__(self, image_link_re, md, base_path):
        self.base_path = base_path

        super(_MarkdownImageProcessor, self).__init__(image_link_re, md)

    def handleMatch(self, match, data):
        image, start, index = super().handleMatch(match, data)

        if image is None or not image.get('title'):
            return image, start, index

        src = image.get('src')
        caption = image.get('title')

        if src.startswith('http'):
            raise ValueError(f'Image path {src} has been given. Only images '
                             'available on the file system can be added.')

        image_path = Path(src)
        if not image_path.is_absolute():
            image_path = (self.base_path / image_path).resolve()

        url = webviz_assets.add(image_path)

        image_style = ''
        for style_prop in image.get('alt').split(','):
            prop, value = style_prop.split('=')
            if prop == 'width':
                image_style += f'width: {value};'
            elif prop == 'height':
                image_style += f'height: {value};'

        if image_style:
            image.set('style', image_style)

        image.set('src', url)
        image.set('class', '_markdown_image')

        container = etree.Element('span')
        container.append(image)

        etree.SubElement(container,
                         'span',
                         attrib={'class': '_markdown_image_caption'}
                         ).text = caption

        return container, start, index


class Markdown(WebvizContainer):
    '''### Include Markdown

_Note:_ The markdown syntax for images has been extended to support
(optionally) providing width and/or height for individual images.
To specify the dimensions write e.g.
```markdown
![width=40%,height=300px](./example_banner.png "Some caption")
```

This container renders and includes the content from a Markdown file. Images
are supported, and should in the markdown file be given as either relative
paths to the markdown file itself, or absolute paths.

* `markdown_file`: Path to the markdown file to render and include. Either
  absolute path or relative to the configuration file.
'''

    ALLOWED_TAGS = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'b', 'i', 'strong', 'em', 'tt',
        'p', 'br', 'span', 'div', 'blockquote', 'code', 'hr',
        'ul', 'ol', 'li', 'dd', 'dt', 'img', 'a', 'sub', 'sup',
        'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]

    ALLOWED_ATTRIBUTES = {
        '*': ['id', 'class', 'style'],
        'img': ['src', 'alt', 'title', 'style'],
        'a': ['href', 'alt', 'title']
    }

    ALLOWED_STYLES = ['width', 'height']

    def __init__(self, markdown_file: Path):

        self.markdown_file = markdown_file

        self.html = bleach.clean(
                        markdown.markdown(
                            get_path(self.markdown_file).read_text(),
                            extensions=['tables',
                                        'sane_lists',
                                        _WebvizMarkdownExtension(
                                            base_path=markdown_file.parent
                                                                 )]),
                        tags=Markdown.ALLOWED_TAGS,
                        attributes=Markdown.ALLOWED_ATTRIBUTES,
                        styles=Markdown.ALLOWED_STYLES
                                )

    def add_webvizstore(self):
        return [(get_path, [{'path': self.markdown_file}])]

    @property
    def layout(self):
        return html.Markdown(self.html, dangerously_allow_html=True)


@webvizstore
def get_path(path) -> Path:
    return path

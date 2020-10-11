import re
from pathlib import Path
from typing import List
from xml.etree import ElementTree  # nosec

import bleach
import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import ImageInlineProcessor, IMAGE_LINK_RE
import dash_core_components as dcc

from .. import WebvizPluginABC
from ..webviz_assets import WEBVIZ_ASSETS
from ..webviz_store import webvizstore


class _WebvizMarkdownExtension(Extension):
    def __init__(self, base_path: Path):
        self.base_path = base_path

        super().__init__()

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.inlinePatterns.register(  # type: ignore[attr-defined]
            item=_MarkdownImageProcessor(IMAGE_LINK_RE, md, self.base_path),
            name="image_link",
            priority=50,
        )


class _MarkdownImageProcessor(ImageInlineProcessor):
    def __init__(self, image_link_re: str, md: markdown.core.Markdown, base_path: Path):
        self.base_path = base_path

        super().__init__(image_link_re, md)

    def handleMatch(self, m, data: str) -> tuple:  # type: ignore[no-untyped-def]
        image, start, index = super().handleMatch(m, data)

        if image is None or not image.get("title"):
            return image, start, index

        src = image.get("src")
        caption = image.get("title")

        if src.startswith("http"):
            raise ValueError(
                f"Image path {src} has been given. Only images "
                "available on the file system can be added."
            )

        image_path = Path(src)

        if not image_path.is_absolute():
            image_path = (self.base_path / image_path).resolve()

        url = WEBVIZ_ASSETS.add(image_path)

        image_style = ""
        for style_prop in image.get("alt").split(","):
            prop, value = style_prop.split("=")
            if prop == "width":
                image_style += f"width: {value};"
            elif prop == "height":
                image_style += f"height: {value};"

        if image_style:
            image.set("style", image_style)

        image.set("src", url)
        image.set("class", "_markdown_image")

        container = ElementTree.Element("span")
        container.append(image)

        ElementTree.SubElement(
            container, "span", attrib={"class": "_markdown_image_caption"}
        ).text = caption

        return container, start, index


class Markdown(WebvizPluginABC):
    """Renders and includes the content from a Markdown file.

    ---

    * **`markdown_file`:** Path to the markdown file to render and include. \
                        Either absolute path or relative to the configuration file.

    ---

    Images are supported, and should in the markdown file be given as either
    relative paths to the markdown file itself, or as absolute paths.

    > The markdown syntax for images has been extended to support \
    providing width and/or height for individual images (optional). \
    To specify the dimensions write e.g.
    > ```markdown
    > ![width=40%,height=300px](./example_banner.png "Some caption")
    > ```

    """

    ALLOWED_TAGS = [
        "a",
        "b",
        "blockquote",
        "br",
        "cite",
        "code",
        "dd",
        "del",
        "details",
        "div",
        "dl",
        "dt",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "i",
        "img",
        "ins",
        "li",
        "mark",
        "ol",
        "p",
        "pre",
        "q",
        "s",
        "span",
        "strong",
        "sub",
        "summary",
        "sup",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
        "ul",
    ]

    ALLOWED_ATTRIBUTES = {
        "*": ["id", "class", "style"],
        "a": ["href", "alt", "title"],
        "details": ["open"],
        "img": ["src", "alt", "title", "style"],
        "li": ["value"],
        "ol": ["reversed", "start", "type"],
        "td": ["colspan", "rowspan"],
        "th": ["colspan", "rowspan", "scope"],
    }

    ALLOWED_STYLES = ["width", "height"]

    def __init__(self, markdown_file: Path):

        super().__init__()

        self.markdown_file = markdown_file

        self.html = bleach.clean(
            markdown.markdown(
                get_path(self.markdown_file).read_text(),
                extensions=[
                    "tables",
                    "sane_lists",
                    _WebvizMarkdownExtension(base_path=markdown_file.parent),
                ],
            ),
            tags=Markdown.ALLOWED_TAGS,
            attributes=Markdown.ALLOWED_ATTRIBUTES,
            styles=Markdown.ALLOWED_STYLES,
        )

        # Workaround for upstream issue https://github.com/plotly/dash-core-components/issues/746,
        # where we convert void html tags from <tag> to <tag/>.
        self.html = re.sub("<img (.*?[^/])>", r"<img \1/>", self.html)
        self.html = self.html.replace("<br>", "<br/>").replace("<hr>", "<hr/>")

    def add_webvizstore(self) -> List[tuple]:
        return [(get_path, [{"path": self.markdown_file}])]

    @property
    def layout(self) -> dcc.Markdown:
        return dcc.Markdown(self.html, dangerously_allow_html=True)


@webvizstore
def get_path(path: Path) -> Path:
    return path

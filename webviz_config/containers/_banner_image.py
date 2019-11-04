from pathlib import Path

import dash_html_components as html

from .. import WebvizContainerABC
from ..webviz_assets import WEBVIZ_ASSETS


class BannerImage(WebvizContainerABC):
    """### Banner image

This container adds a full width _banner image_, with an optional overlayed
title. Useful on e.g. the front page for introducing a field or project.

* `image`: Path to the picture you want to add. Either absolute path or
  relative to the configuration file.
* `title`: Title which will be overlayed over the banner image.
* `color`: Color to be used for the font.
* `shadow`: Set to `False` if you do not want text shadow for the title.
* `height`: Height of the banner image (in pixels).
"""

    TOOLBAR_BUTTONS = []

    def __init__(
        self,
        image: Path,
        title: str = "",
        color: str = "white",
        shadow: bool = True,
        height: int = 300,
    ):

        self.image = image
        self.title = title
        self.color = color
        self.shadow = shadow
        self.height = height

        self.image_url = WEBVIZ_ASSETS.add(image)

    @property
    def layout(self):

        style = {
            "color": self.color,
            "background-image": f"url({self.image_url})",
            "height": f"{self.height}px",
        }

        if self.shadow:
            style["text-shadow"] = "0.05em 0.05em 0"

            if self.color == "white":
                style["text-shadow"] += " rgba(0, 0, 0, 0.7)"
            else:
                style["text-shadow"] += " rgba(255, 255, 255, 0.7)"

        return html.Div(self.title, className="_banner_image", style=style)

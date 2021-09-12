from pathlib import Path
from typing import List

from dash import html

from .. import WebvizPluginABC
from ..webviz_assets import WEBVIZ_ASSETS


class BannerImage(WebvizPluginABC):
    """Adds a full width banner image, with an optional overlayed title.
Useful on e.g. the front page for introducing a field or project.

---

* **`image`:** Path to the picture you want to add. \
               Either absolute path or relative to the configuration file.
* **`title`:** Title which will be overlayed over the banner image.
* **`color`:** Color to be used for the font.
* **`shadow`:** Set to `False` if you do not want text shadow for the title.
* **`height`:** Height of the banner image (in pixels).
"""

    TOOLBAR_BUTTONS: List[str] = []

    def __init__(
        self,
        image: Path,
        title: str = "",
        color: str = "white",
        shadow: bool = True,
        height: int = 300,
    ):

        super().__init__()

        self.image = image
        self.title = title
        self.color = color
        self.shadow = shadow
        self.height = height

        self.image_url = WEBVIZ_ASSETS.add(image)

    @property
    def layout(self) -> html.Div:

        style = {
            "color": self.color,
            "backgroundImage": f"url({self.image_url})",
            "height": f"{self.height}px",
        }

        if self.shadow:
            style["textShadow"] = "0.05em 0.05em 0"

            if self.color == "white":
                style["textShadow"] += " rgba(0, 0, 0, 0.7)"
            else:
                style["textShadow"] += " rgba(255, 255, 255, 0.7)"

        return html.Div(self.title, className="_banner_image", style=style)

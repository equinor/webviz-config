from pathlib import Path
from typing import Dict

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
* **`title_position`:** Position of title (either `center`, `top` or `bottom`).
"""

    CSS_TITLE_POSITIONS: Dict[str, str] = {
        "top": "start",
        "center": "center",
        "bottom": "end",
    }

    def __init__(
        self,
        image: Path,
        title: str = "",
        color: str = "white",
        shadow: bool = True,
        height: int = 300,
        title_position: str = "center",
    ):

        super().__init__()

        self.image = image
        self.title = title
        self.color = color
        self.shadow = shadow
        self.height = height

        try:
            self.css_title_position = BannerImage.CSS_TITLE_POSITIONS[title_position]
        except KeyError as exc:
            raise ValueError(
                f"{title_position} not a valid position for banner image title. "
                f"Valid options: {', '.join(BannerImage.CSS_TITLE_POSITIONS.keys())}"
            ) from exc

        self.image_url = WEBVIZ_ASSETS.add(image)

    @property
    def layout(self) -> html.Div:

        style = {
            "color": self.color,
            "backgroundImage": f"url({self.image_url})",
            "height": f"{self.height}px",
            "align-items": self.css_title_position,
        }

        if self.shadow:
            style["textShadow"] = "0.05em 0.05em 0"

            if self.color == "white":
                style["textShadow"] += " rgba(0, 0, 0, 0.7)"
            else:
                style["textShadow"] += " rgba(255, 255, 255, 0.7)"

        return html.Div(self.title, className="_banner_image", style=style)

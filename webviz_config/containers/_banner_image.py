import os
from pathlib import Path
import dash_html_components as html
from ..webviz_assets import webviz_assets


class BannerImage:
    '''### Banner image

This container adds a full width _banner image_, with an optional overlayed
title. Useful on e.g. the front page for introducing a field or project.

* `image`: Path to the picture you want to add. Either absolute path or
  relative to the configuration file.
* `title`: Title which will be overlayed over the banner image.
* `color`: Color to be used for the font.
* `shadow`: Set to `False` if you do not want text shadow for the title.
'''

    def __init__(self, image: Path, title: str = '', color: str = 'white',
                 shadow: bool = True):

        self.image = image
        self.title = title
        self.color = color
        self.shadow = shadow

        self.image_url = webviz_assets.add(image)

    @property
    def layout(self):

        style = {'color': self.color,
                 'background-image': 'url({})'.format(self.image_url)}

        if self.shadow:
            style['text-shadow'] = '0.05em 0.05em 0'

            if self.color == 'white':
                style['text-shadow'] += ' rgba(0, 0, 0, 0.7)'
            else:
                style['text-shadow'] += ' rgba(255, 255, 255, 0.7)'

        return html.Div(self.title, className='_banner_image', style=style)

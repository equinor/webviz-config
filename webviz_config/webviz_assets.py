import re
import os
import shutil
import pathlib

import flask

from .utils import terminal_colors


class WebvizAssets:
    """Dash applications by default host static resources from a folder called
    ./assets, relative to the root application folder.

    In order to facilitate hot reloading, and fast building of Webviz
    applications from the configuration file, this class facilitates handling
    of static assets.

    Individual plugins can add assets to a common instance of WebvizAssets
    by calling the .add(filename) function. This adds the resource, and
    at the same time returns the resource URI which the plugin can use.

    If the webviz instance is in non-portable mode, the Flask/Dash application
    is routed to the actual location of the files, making hot reload and
    testing fast.

    When creating a portable webviz instance however, the files are copied
    over the ./assets folder, and normal Dash usage applies.

    In both portable and non-portable mode, WebvizAssets makes sure there are
    no name conflicts (i.e. it supports multiple assets on different paths,
    but with same filename) and also assignes URI friendly resource IDs.
    """

    def __init__(self):
        self._assets = {}
        self._portable = False

    @property
    def portable(self):
        return self._portable

    @portable.setter
    def portable(self, portable):
        self._portable = portable

    def _base_folder(self):
        return "assets" if self.portable else "temp"

    def add(self, filename):
        path = pathlib.Path(filename)

        if filename not in self._assets.values():
            assigned_id = self._generate_id(path.name)
            self._assets[assigned_id] = filename
        else:
            assigned_id = {v: k for k, v in self._assets.items()}[filename]

        return os.path.normcase(os.path.join(self._base_folder(), assigned_id))

    def register_app(self, app):
        """In non-portable mode, this function can be called by the
        application. It routes the Dash application to the added assets on
        disk, making hot reloading and more interactive development of the
        application possible.
        """

        @app.server.route(f"/{self._base_folder()}/<path:asset_id>")
        def _send_file(asset_id):
            if asset_id in self._assets:  # Only serve white listed resources
                path = pathlib.Path(self._assets[asset_id])
                return flask.send_from_directory(path.parent, path.name)
            return None

    def make_portable(self, asset_folder):
        """Copy over all added assets to the given folder (asset_folder).
        """

        for counter, (assigned_id, filename) in enumerate(self._assets.items()):
            print(
                f"{terminal_colors.PURPLE} Copying over {filename} {terminal_colors.END}",
                end="",
                flush=True,
            )

            shutil.copyfile(filename, os.path.join(asset_folder, assigned_id))

            print(
                f"{terminal_colors.PURPLE}{terminal_colors.BOLD} "
                f"[\u2713] Copied ({counter + 1}/{len(self._assets)})"
                f"{terminal_colors.END}"
            )

    def _generate_id(self, filename):
        """From the filename, create a safe resource id not already present
        """
        asset_id = base_id = re.sub(
            "[^-a-z0-9._]+", "", filename.lower().replace(" ", "_")
        )

        count = 1
        while asset_id in self._assets:
            count += 1
            asset_id = f"{base_id}{count}"

        return asset_id


WEBVIZ_ASSETS = WebvizAssets()

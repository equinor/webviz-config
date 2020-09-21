import re
import shutil
import pathlib
from typing import Optional

from tqdm import tqdm
from dash import Dash
import flask


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

    def __init__(self) -> None:
        self._assets: dict = {}
        self._portable = False

    @property
    def portable(self) -> bool:
        return self._portable

    @portable.setter
    def portable(self, portable: bool) -> None:
        self._portable = portable

    def _base_folder(self) -> str:
        return "assets" if self.portable else "temp"

    def add(self, filename: pathlib.Path) -> str:
        """Calling this function makes the filename given as input
        available as a hosted asset when the application is running.
        The returned string is a URI which the plugin optionally
        can use internally (e.g. as "src" in image elements).

        Calling this function with the same input path
        multiple times will return the same URI.

        Filenames added to WebvizAssets that ends with .css or .js
        are loaded automatically in the browser by Dash,
        both in non-portable and portable mode.
        """

        path = pathlib.Path(filename)

        if filename not in self._assets.values():
            assigned_id = self._generate_id(path.name)
            self._assets[assigned_id] = filename
        else:
            assigned_id = {v: k for k, v in self._assets.items()}[filename]

        return str(pathlib.Path(self._base_folder()) / assigned_id)

    def directly_host_assets(self, app: Dash) -> None:
        """In non-portable mode, this function can be called by the
        application. It routes the Dash application to the added assets on
        disk, making hot reloading and more interactive development of the
        application possible.
        """

        if self._portable:
            raise RuntimeError(
                "The function WebvizAssets.directly_host_assets() "
                "method is only meaningful in a non-portable settings."
            )

        @app.server.route(f"/{self._base_folder()}/<path:asset_id>")
        def _send_file(asset_id: str) -> Optional[flask.wrappers.Response]:
            if asset_id in self._assets:  # Only serve white listed resources
                path = pathlib.Path(self._assets[asset_id])
                return flask.send_from_directory(path.parent, path.name)
            return None

        # Add .css and .js files to auto-loaded Dash assets
        for asset_id, asset_path in self._assets.items():
            if asset_path.suffix == ".css":
                app.config.external_stylesheets.append(
                    f"./{self._base_folder()}/{asset_id}"
                )
            elif asset_path.suffix == ".js":
                app.config.external_scripts.append(
                    f"./{self._base_folder()}/{asset_id}"
                )

    def make_portable(self, asset_folder: pathlib.Path) -> None:
        """Copy over all added assets to the given folder (asset_folder)."""

        for assigned_id, filename in tqdm(
            self._assets.items(),
            bar_format="{l_bar} {bar} | Copied {n_fmt}/{total_fmt}",
        ):
            tqdm.write(f"Copying over {filename}")
            shutil.copyfile(filename, asset_folder / assigned_id)

    def _generate_id(self, filename: str) -> str:
        """From the filename, create a safe resource id not already present"""
        asset_id = base_id = re.sub(
            "[^-a-z0-9._]+", "", filename.lower().replace(" ", "_")
        )

        count = 1
        while asset_id in self._assets:
            count += 1
            asset_id = f"{base_id}{count}"

        return asset_id


WEBVIZ_ASSETS = WebvizAssets()

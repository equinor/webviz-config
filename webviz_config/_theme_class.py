import copy
import json


class WebvizConfigTheme:
    """Webviz config themes are all instances of this class. The only mandatory
    property is the theme name set at initialization.
    """

    def __init__(self, theme_name: str):
        self.theme_name = theme_name

        self._csp = {
            "default-src": "'none'",
            "connect-src": "'self'",
            "prefetch-src": "'self'",
            "style-src": ["'self'", "'unsafe-inline'"],  # [1]
            "script-src": [
                "'self'",
                "'unsafe-eval'",  # [2]
            ],
            "img-src": ["'self'", "data:", "blob:"],  # [3]
            "navigate-to": "'self'",
            "base-uri": "'self'",
            "form-action": "'self'",
            "frame-ancestors": "'self'",  # [4]
            "frame-src": "'self'",  # [4]
            "object-src": "'self'",
            "plugin-types": "application/pdf",
        }

        """
        These are the current exceptions to the most strict CSP setup:
            [1] unsafe-inline for style still needed by plotly
                (https://github.com/plotly/plotly.js/issues/2355)
            [2] unsafe-eval still needed for plotly.js bundle
                (https://github.com/plotly/plotly.js/issues/897)
            [3] html2canvas in webviz-core-components needs "data:" in img-src to create
                screenshots, while plotly.js "Download screenshot to png" requires
                "blob:" in img-src.
            [4] We use 'self' instead of 'none' due to what looks like a Chromium bug,
                where e.g. pdf's included using <embed> is not rendered. Might be
                related to https://bugs.chromium.org/p/chromium/issues/detail?id=1002610
        """

        self._feature_policy = {
            "camera": "'none'",
            "geolocation": "'none'",
            "microphone": "'none'",
            "payment": "'none'",
        }

        self._external_stylesheets: list = []
        self._assets: list = []
        self._plotly_theme: dict = {}

    def to_json(self) -> str:
        return json.dumps(vars(self), indent=4, sort_keys=True)

    def from_json(self, json_string: str) -> None:
        for key, value in json.loads(json_string).items():
            setattr(self, key, value)

    def adjust_csp(self, dictionary: dict, append: bool = True) -> None:
        """If the default CSP settings needs to be changed, this function can
        be called by giving in a dictionary with key-value pairs which should
        be changed. If `append=True`, the CSP sources given in the dictionary
        are appended to the whitelisted sources in the default configuration.
        If not the input value source list is instead replacing the default
        whitelisted sources.
        """

        for key, value in dictionary.items():
            if append and key in self._csp:
                self._csp[key] += value
            else:
                self._csp[key] = value

    def create_themed_layout(self, layout: dict) -> dict:
        """
        Create a new Plotly layout dict by merging the input layout with the theme layout,
        prioritizing the input layout if there are conflicts with the theme layout. In addition:
        For the special case of multiple xaxes or yaxes, e.g. xaxis2 and xaxis3 (for a secondary
        and tertiary xaxis), the axis will get the theme xaxis/yaxis layout, unless they are
        defined themselves as e.g. xaxis2 in the theme layout. Note that e.g. xaxis2 still needs to
        be in the input layout, just not in the theme layout.
        """
        # pylint: disable=too-many-nested-blocks
        def deep_update(update: dict, ref: dict) -> dict:
            for key, value in ref.items():
                if key in update:
                    if isinstance(value, dict):
                        if isinstance(update[key], dict):
                            update[key] = deep_update(update[key], value)
                        if key in ["xaxis", "yaxis"]:
                            for kkey in update:
                                if kkey not in ref and kkey.startswith(key):
                                    update[kkey] = deep_update(update[kkey], value)
                else:
                    update[key] = value
            return update

        return deep_update(
            copy.deepcopy(layout), copy.deepcopy(self._plotly_theme["layout"])
        )

    @property
    def csp(self) -> dict:
        """Returns the content security policy settings for the theme."""
        return self._csp

    @property
    def feature_policy(self) -> dict:
        """Returns the feature policy settings for the theme."""
        return self._feature_policy

    @property
    def plotly_theme(self) -> dict:
        return copy.deepcopy(self._plotly_theme)

    @plotly_theme.setter
    def plotly_theme(self, plotly_theme: dict) -> None:
        """Layout object of Plotly graph objects."""
        self._plotly_theme = plotly_theme

    @property
    def external_stylesheets(self) -> list:
        return self._external_stylesheets

    @external_stylesheets.setter
    def external_stylesheets(self, external_stylesheets: list) -> None:
        """Set optional external stylesheets to be used in the Dash
        application. The input variable `external_stylesheets` should be
        a list."""
        self._external_stylesheets = external_stylesheets

    @property
    def assets(self) -> list:
        return self._assets

    @assets.setter
    def assets(self, assets: list) -> None:
        """Set optional theme assets to be copied over to the `./assets` folder
        when the webviz dash application is created. The input variable
        `assets` should be a list of absolute file paths to the different
        assets.
        """
        self._assets = assets

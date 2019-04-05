CSP = {
    'default-src': '\'self\'',
    'prefetch-src': '\'self\'',
    'style-src': ['\'self\'', '\'unsafe-inline\''],  # [1]
    'script-src': ['\'self\'', '\'unsafe-eval\'',  # [2]
                   '\'sha256-jZlsGVOhUAIcH+4PV'\
                   's7QuGZkthRMgvT2n0ilH6/zTM0=\''],  # [3]
    'img-src': ['\'self\'', 'data:'],
    'navigate-to': '\'self\'',
    'base-uri': '\'self\'',
    'form-action': '\'self\'',
    'frame-ancestors': '\'none\'',
    'object-src': '\'none\'',
}

'''
These are the current exceptions to the most strict CSP setup:
[1] unsafe-inline for style still needed by plotly
    (https://github.com/plotly/plotly.js/issues/2355)
[2] unsafe-eval still needed by plotly
    (https://github.com/plotly/plotly.js/issues/897)
[3] https://github.com/plotly/dash/issues/630
'''

FEATURE_POLICY = {'camera': '\'none\'',
                  'geolocation': '\'none\'',
                  'microphone': '\'none\'',
                  'payment': '\'none\''}


class WebvizConfigTheme:
    """Webviz config themes are all instances of this class. The only mandatory
    property is the theme name set at initialization.
    """

    def __init__(self, theme_name):
        self.theme_name = theme_name

        self._csp = CSP
        self._feature_policy = FEATURE_POLICY
        self._external_stylesheets = []
        self._assets = []

    def adjust_csp(self, dictionary, append=True):
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

    @property
    def csp(self):
        """Returns the content security policy settings for the theme"""
        return self._csp

    @property
    def feature_policy(self):
        """Returns the feature policy settings for the theme"""
        return self._feature_policy

    @property
    def external_stylesheets(self):
        return self._external_stylesheets

    @external_stylesheets.setter
    def external_stylesheets(self, external_stylesheets):
        """Set optional external stylesheets to be used in the Dash
        application. The input variable `external_stylesheets` should be
        a list."""
        self._external_stylesheets = external_stylesheets

    @property
    def assets(self):
        return self._assets

    @assets.setter
    def assets(self, assets):
        """Set optional theme assets to be copied over to the `./assets` folder
        when the webviz dash application is created. The input variable
        `assets` should be a list of absolute file paths to the different
        assets.
        """
        self._assets = assets

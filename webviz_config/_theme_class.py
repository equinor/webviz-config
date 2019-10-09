class WebvizConfigTheme:
    """Webviz config themes are all instances of this class. The only mandatory
    property is the theme name set at initialization.
    """

    def __init__(self, theme_name):
        self.theme_name = theme_name

        self._csp = {
            "default-src": "'none'",
            "connect-src": "'self'",
            "prefetch-src": "'self'",
            "style-src": [
                "'self'",
                "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",
                "'sha256-0nyLRBz+flfRx09c4cmwCuyAActw00JI7EotsctBGyE='",
                "'sha256-xvTswO0KvrqfuIznkf9xZZjHWjEInO6xAR8R0i9cNXE='",
                "'sha256-zv5T/1jqVSYAZNyuFq6Oe3myEs6fWtJrbBVVlyod0pI='",
                "'sha256-bz067pWUhHiNnuT7QqKF7WbiR/HbE5cZpiNGvKjEtL8='",
                "'sha256-j1Z3vG9BYlqSP0PAgKRPVALn3N+OyHEXESbZCB9a3/Y='",
                "'sha256-vcfrXKQsmXUbUpLQEav11i3ibKFKxzWl5AbZj1Mi7BA='",
                "'sha256-n0t2e/d3b3uV1Tpz1LxUHhirqiz3PjozVhgIrya3wUw='",
                "'sha256-cJ5ObsneXZnEJ3xXl8hpmaM9RbOwaU6UIPslFf0/OOE='",
                "'sha256-8IiIAtdYJmcaYoCMc+jEFonF7lY2IqEZsapB3vR06+0='",
                "'sha256-7HmiKdPrXkgSHu/bLW+h89afE8m7fLOzXpWM/WLkwRY='",
                "'sha256-MKz8DWR0f5EtPWPAQ1fbaoAcdd9nMWG2532Ea6DTX1I='",
                "'sha256-chHWcINw1Gl2Po6c1IhNWVPCqSX0gwpI+B5NbBGpKe4='",
                "'sha256-SOIvgny/o7VdEcLthH5zNQbMT58PRGaiR7gQrgsNGwY='",
                "'sha256-iWKLqOVfl1am1pYdv28h164kO8lv+Yzb2G3XY5btpXY='",
                "'sha256-joa3+JBk4cwm5iLfizxl9fClObT5tKuZMFQ9B2FZlMg='",
                "'sha256-MAsOH+5AggnYmMaZv+hjrdQ22FV6k4b4GnNZjn76hfI='",
                "'sha256-Jtp4i67c7nADbaBCKBYgqI86LQOVcoZ/khTKsuEkugc='",
                "'sha256-MoQFjm6Ko0VvKSJqNGTl4e5H3guejX+CG/LxytSdnYg='",
                "'sha256-Hhrf0PLsXNnfugTF8pcjTS09SrwRiMN+/e4/Lc8mTIw='",
                "'sha256-Bgj5ZRruQPZA0MeFtY6SdF1i4JCe/xePw0jvKF7Nwm0='",
            ],
            "script-src": [
                "'self'",
                "'sha256-jZlsGVOhUAIcH+4PVs7QuGZkthRMgvT2n0ilH6/zTM0='",
            ],  # [2]
            "img-src": ["'self'", "data:"],
            "navigate-to": "'self'",
            "base-uri": "'self'",
            "form-action": "'self'",
            "frame-ancestors": "'none'",
            "child-src": "'none'",
            "object-src": "'self'",
            "plugin-types": "application/pdf",
        }

        """
        These are the current exceptions to the most strict CSP setup:
            [1] unsafe-inline for style still needed by plotly
                (https://github.com/plotly/plotly.js/issues/2355)
            [2] https://github.com/plotly/dash/issues/630
        """

        self._feature_policy = {
            "camera": "'none'",
            "geolocation": "'none'",
            "microphone": "'none'",
            "payment": "'none'",
        }

        self._external_stylesheets = []
        self._assets = []
        self._plotly_layout = {}

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
        """Returns the content security policy settings for the theme."""
        return self._csp

    @property
    def feature_policy(self):
        """Returns the feature policy settings for the theme."""
        return self._feature_policy

    @property
    def plotly_layout(self):
        return self._plotly_layout

    @plotly_layout.setter
    def plotly_layout(self, plotly_layout):
        """Layout object of Plotly graph objects."""
        self._plotly_layout = plotly_layout

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

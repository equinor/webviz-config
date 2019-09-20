import secrets
import flask


class LocalhostLogin:

    def __init__(self, app, ott=None, cookie_token=None):
        self._app = app

        # This is the cookie token set in the users browser after
        # successfully providing the one time token
        self._cookie_token = LocalhostLogin.generate_token() \
            if cookie_token is None else cookie_token

        # The one time token user has to provide when visiting the
        # localhost app the first time.
        self._ott = LocalhostLogin.generate_token() if ott is None else ott
        self._ott_validated = False

        self.set_request_decorators()

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(nbytes=64)

    @property
    def one_time_token(self):
        return self._ott

    def set_request_decorators(self):

        @self._app.before_request
        def _check_for_ott_or_cookie():
            if not self._ott_validated \
                    and self._ott == flask.request.args.get('ott'):
                self._ott_validated = True
                flask.g.set_cookie_token = True
                return flask.redirect(flask.request.base_url)
            elif self._cookie_token \
                    == flask.request.cookies.get('cookie_token'):
                self._ott_validated = True
            else:
                flask.abort(401)

        @self._app.after_request
        def _set_cookie_token_in_response(response):
            if 'set_cookie_token' in flask.g and flask.g.set_cookie_token:
                response.set_cookie(
                    key='cookie_token',
                    value=self._cookie_token
                )
            return response

import secrets
import flask

class LocalhostLogin:
    
    def __init__(self, app):
        self._app = app
        self._cookie_token = secrets.token_urlsafe()

        self._ott = secrets.token_urlsafe()
        self._ott_used = False

        self.set_callbacks(self._app)

    @property
    def one_time_token(self):
        return self._ott

    def set_callbacks(self, app):

        @app.before_request
        def before_request_func():
            if not self._ott_used and self._ott == flask.request.args.get('ott'):
                self._ott_used = True
                flask.g.set_cookie_token = True
            elif self._cookie_token != flask.request.cookies.get('cookie_token'):
                flask.abort(401)

        @app.after_request
        def set_language_cookie(response):
            if 'set_cookie_token' in flask.g and flask.g.set_cookie_token:
                response.set_cookie('cookie_token', value=self._cookie_token)

            return response

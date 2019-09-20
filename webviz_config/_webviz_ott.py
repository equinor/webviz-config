import secrets
import flask

class LocalhostLogin:
    
    def __init__(self, app):
        self._app = app

        # This is the cookie token set in the users browser after
        # successfully providing the one time token
        self._cookie_token = secrets.token_urlsafe()

        # The one time token user has to provide when visiting the
        # localhost app the first time.
        self._ott = secrets.token_urlsafe()
        self._ott_used = False

        self.set_request_decorators()

    @property
    def one_time_token(self):
        return self._ott

    def set_request_decorators(self):

        @self._app.before_request
        def check_for_ott_or_cookie():
            if not self._ott_used and self._ott == flask.request.args.get('ott'):
                self._ott_used = True
                flask.g.set_cookie_token = True
            elif self._cookie_token != flask.request.cookies.get('cookie_token'):
                flask.abort(401)

        @self._app.after_request
        def set_cookie_token_in_response(response):
            if 'set_cookie_token' in flask.g and flask.g.set_cookie_token:
                response.set_cookie('cookie_token', value=self._cookie_token)

            return response

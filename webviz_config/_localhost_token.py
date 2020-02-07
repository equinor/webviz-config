import os
import secrets

import flask

from ._is_reload_process import is_reload_process


class LocalhostToken:
    """Uses a method similar to jupyter notebook (however, here we do it over
    https in addition). This method is only used during interactive usage on
    localhost, and the workflow is as follows:

    - During the flask app building, a one-time-token (ott) and a cookie_token
      is generated.
    - When the app is ready, the user needs to "login" using this
      one-time-token in the url (https://localhost:{port}?ott={token})
    - If ott is valid - a cookie with a separate token is set, and the
      one-time-token is discarded. The cookie is then used for subsequent
      requests.

    If the user fails both providing a valid one-time-token and a valid cookie
    token, all localhost requests gets a 401.

    If the app is in non-portable mode, the one-time-token and
    cookie token  are reused on app reload (in order to ensure live reload
    works without requiring new login).

    The port is used as a postfix on the cookie name in order to make sure that
    two different localhost applications running simultaneously do not interfere.
    """

    def __init__(self, app: flask.app.Flask, port: int):
        self._app = app
        self._port = port

        if not is_reload_process():
            # One time token (per run) user has to provide
            # when visiting the localhost app the first time.
            self._ott = os.environ["WEBVIZ_OTT"] = LocalhostToken.generate_token()

            # This is the cookie token set in the users browser after
            # successfully providing the one time token
            self._cookie_token = os.environ[
                "WEBVIZ_COOKIE_TOKEN"
            ] = LocalhostToken.generate_token()

        else:
            self._ott = os.environ["WEBVIZ_OTT"]
            self._cookie_token = os.environ["WEBVIZ_COOKIE_TOKEN"]

        self._ott_validated = False
        self.set_request_decorators()

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(nbytes=64)

    @property
    def one_time_token(self) -> str:
        return self._ott

    def set_request_decorators(self) -> None:
        # pylint: disable=inconsistent-return-statements
        @self._app.before_request
        def _check_for_ott_or_cookie():  # type: ignore[no-untyped-def]
            if not self._ott_validated and self._ott == flask.request.args.get("ott"):
                self._ott_validated = True
                flask.g.set_cookie_token = True
                return flask.redirect(flask.request.base_url)

            if self._cookie_token == flask.request.cookies.get(
                f"cookie_token_{self._port}"
            ):
                self._ott_validated = True
            else:
                flask.abort(401)

        @self._app.after_request
        def _set_cookie_token_in_response(
            response: flask.wrappers.Response,
        ) -> flask.wrappers.Response:
            if "set_cookie_token" in flask.g and flask.g.set_cookie_token:
                response.set_cookie(
                    key=f"cookie_token_{self._port}", value=self._cookie_token
                )
            return response

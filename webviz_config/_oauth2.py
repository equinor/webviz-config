import os
import datetime
from typing import Tuple

import msal
import flask


class Oauth2:
    """Oauth2 authorization Code grant flow"""

    def __init__(self, app: flask.app.Flask):
        self._app = app

        # Azure AD app registration info (currently the values are taken from environment variables)
        self._tenant_id = os.environ["WEBVIZ_TENANT_ID"]
        self._client_id = os.environ["WEBVIZ_CLIENT_ID"]
        self._client_secret = os.environ["WEBVIZ_CLIENT_SECRET"]
        self._scope = os.environ["WEBVIZ_SCOPE"]

        # Initiate msal
        self._msal_app = msal.ConfidentialClientApplication(
            client_id=self._client_id,
            client_credential=self._client_secret,
            authority=f"https://login.microsoftonline.com/{self._tenant_id}",
        )
        self._accounts = self._msal_app.get_accounts()

        # Initiate oauth2 endpoints
        self.set_oauth2_endpoints()

    def set_oauth2_endpoints(self) -> None:
        """/login and /auth-return endpoints are added for Oauth2 authorization
        code flow.

        At the end of the flow, a session cookie containing a valid access token
        and its expiration date is created. This flask session object can be
        accessed from Webviz plugin.

        To get the access token: flask.session.get("access_token")
        To get the expiration date: flask.session.get("expiration_date")

        An Azure AD application should be registered, and the following environment
        variables should be set: WEBVIZ_TENANT_ID, WEBVIZ_CLIENT_ID,
        WEBVIZ_CLIENT_SECRET, WEBVIZ_SCOPE.
        """

        @self._app.route("/login")
        def _login_controller():  # type: ignore[no-untyped-def]
            redirect_uri = get_auth_redirect_uri(flask.request.url_root)

            # First leg of Oauth2 authorization code flow
            auth_url = self._msal_app.get_authorization_request_url(
                scopes=[self._scope], redirect_uri=redirect_uri
            )
            return flask.redirect(auth_url)

        @self._app.route("/auth-return")
        def _auth_return_controller():  # type: ignore[no-untyped-def]
            redirect_uri = get_auth_redirect_uri(flask.request.url_root)
            returned_query_params = flask.request.args

            # There is an error from the first leg of Oauth2 authorization code flow
            if "error" in returned_query_params:
                error_description = returned_query_params.get("error_description")
                print("Error description:", error_description)
                redirect_error_uri = flask.url_for("error_controller")
                return flask.redirect(redirect_error_uri)

            code = returned_query_params.get("code")

            # Second leg of Oauth2 authorization code flow
            tokens_result = self._msal_app.acquire_token_by_authorization_code(
                code=code, scopes=[self._scope], redirect_uri=redirect_uri
            )
            expires_in = tokens_result.get("expires_in")
            expiration_date = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(seconds=expires_in - 60)
            print("Access token expiration date (UTC):", expiration_date)

            # Set expiration date in the session
            flask.session["expiration_date"] = expiration_date

            # Set access token in the session
            flask.session["access_token"] = tokens_result.get("access_token")

            return flask.redirect(flask.request.url_root)

        @self._app.route("/error")
        def _error_controller():  # type: ignore[no-untyped-def]
            return "Error"

    def set_oauth2_before_request_decorator(self) -> None:
        """Check access token existence in session cookie before every request.
        If it does not exist, the browser is redirected to /login endpoint.

        If access token exists, its expiration date is checked in session cookie.
        If the current date exceeds its expiration date, a new access token is
        retrieved and set in the session cookie. A new expiration date is also
        set in the session cookie.
        """

        # pylint: disable=inconsistent-return-statements
        @self._app.before_request
        def _check_access_token():  # type: ignore[no-untyped-def]
            # The session of the request does not contain access token, redirect to /login
            is_redirected, redirect_url = self.is_empty_token()
            if is_redirected:
                return flask.redirect(redirect_url)

            # The session contains access token, check its expiration date
            self.check_and_set_token_expiry()

    @staticmethod
    def is_empty_token() -> Tuple[bool, str]:
        if (
            not flask.session.get("access_token")
            and flask.request.path != "/login"
            and flask.request.path != "/auth-return"
        ):
            login_uri = get_login_uri(flask.request.url_root)
            return True, login_uri

        return False, ""

    def check_and_set_token_expiry(self) -> None:
        if flask.session.get("access_token"):
            expiration_date = flask.session["expiration_date"]
            current_date = datetime.datetime.now(datetime.timezone.utc)
            if current_date > expiration_date:
                # Access token has expired
                print("Access token has expired.")
                if not self._accounts:
                    self._accounts = self._msal_app.get_accounts()
                renewed_tokens_result = self._msal_app.acquire_token_silent(
                    scopes=[self._scope], account=self._accounts[0]
                )
                expires_in = renewed_tokens_result.get("expires_in")
                new_expiration_date = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(seconds=expires_in - 60)
                print("New access token expiration date (UTC):", new_expiration_date)

                # Set new expiration date in the session
                flask.session["expiration_date"] = new_expiration_date

                # Set new access token in the session
                flask.session["access_token"] = renewed_tokens_result.get(
                    "access_token"
                )


def get_login_uri(url_root: str) -> str:
    return url_root + "login"


def get_auth_redirect_uri(url_root: str) -> str:
    return url_root + "auth-return"

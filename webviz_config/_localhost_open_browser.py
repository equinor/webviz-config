import os
import time
import urllib
import threading
import webbrowser

from ._is_reload_process import is_reload_process
from .utils import terminal_colors


class LocalhostOpenBrowser:
    # pylint: disable=too-few-public-methods

    def __init__(self, port, token):
        self._port = port
        self._token = token

        if not is_reload_process():
            # Only open new browser tab if not a reload process
            threading.Thread(target=self._timer).start()

    def _timer(self):
        """Waits until the app is ready, and then opens the page
        in the default browser.
        """

        timeout = 120  # maximum number of seconds to wait before timeout

        for _ in range(timeout):
            if self._app_ready():
                self._open_new_tab()
                return

            time.sleep(1)

        print(
            f"WARNING: Webviz application still not ready after {timeout}s.\n"
            "Will not open browser automatically. Your private one-time login link:\n"
            f"{self._url(with_token=True)}"
        )

    def _url(self, with_token=False, https=True):
        return (
            f"{'https' if https else 'http'}://localhost:{self._port}"
            + f"{'?ott=' + self._token if with_token else ''}"
        )

    @staticmethod
    def _get_browser_controller():
        for browser in ["chrome", "chromium-browser"]:
            try:
                return webbrowser.get(using=browser)
            except webbrowser.Error:
                pass

        # Return default browser if none of the
        # preferred browsers are installed:
        return webbrowser.get()

    def _app_ready(self):
        """Check if the flask instance is ready.
        """

        no_proxy_env = os.environ.get("NO_PROXY")
        os.environ["NO_PROXY"] = "localhost"

        try:
            urllib.request.urlopen(self._url(https=False))  # nosec
            app_ready = True
        except urllib.error.URLError:
            # The flask instance has not started
            app_ready = False
        except ConnectionResetError:
            # The flask instance has started but (correctly) abort
            # request due to "401 Unauthorized"
            app_ready = True
        finally:
            os.environ["NO_PROXY"] = no_proxy_env if no_proxy_env else ""

        return app_ready

    def _open_new_tab(self):
        """Open the url (with token) in the default browser.
        """

        print(
            f"{terminal_colors.GREEN}{terminal_colors.BOLD}"
            f" Opening the application ({self._url()}) in your browser.\n"
            " Press CTRL + C in this terminal window to stop the application."
            f"{terminal_colors.END}"
        )

        LocalhostOpenBrowser._get_browser_controller().open_new_tab(
            self._url(with_token=True)
        )

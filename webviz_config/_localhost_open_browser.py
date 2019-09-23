import os
import time
import urllib
import threading
import webbrowser

from ._is_reload_process import is_reload_process


class LocalhostOpenBrowser:
    def __init__(self, port, token):
        self._port = port
        self._token = token

        self._login_link = f"https://localhost:{self._port}?ott={self._token}"

        if not is_reload_process():
            # Only open new browser tab if not a reload process
            threading.Thread(target=self._timer).start()

    def _timer(self):
        """Waits until the app is ready, and then opens the page
        in the default browser.
        """

        TIMEOUT = 120  # maximum number of seconds to wait before timeout

        for _ in range(TIMEOUT):
            if self._app_ready():
                self._open_new_tab()
                return

            time.sleep(1)

        print(
            f"WARNING: Webviz application still not ready after {TIMEOUT}s.\n"
            "Will not open browser automatically. Your private login link:\n"
            f"{self._login_link}"
        )

    def _app_ready(self):
        """Check if the flask instance is ready.
        """

        no_proxy_env = os.environ.get("NO_PROXY")
        os.environ["NO_PROXY"] = "localhost"

        try:
            urllib.request.urlopen(f"http://localhost:{self._port}")  # nosec
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
            " \n\033[92m"
            " Opening the application in your default browser.\n"
            " Press CTRL+C in this terminal window to stop the application."
            " \033[0m\n"
        )

        webbrowser.open_new_tab(self._login_link)

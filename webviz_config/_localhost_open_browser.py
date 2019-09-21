import os
import time
import urllib
import threading
import webbrowser


class LocalhostOpenBrowser:

    def __init__(self, port, token):
        self._port = port
        self._token = token

        # See Werkzeug documentation. During a flask reload process,
        # the WERKZEUG_RUN_MAIN environment variable is set. During
        # the initial load however it is not set, which is the appropriate time
        # to open the app in the browser.
        if os.environ.get('WERKZEUG_RUN_MAIN') is None:
            threading.Thread(target=self._timer).start()

    def _timer(self):
        '''Waits until the app is ready, and then opens the page
        in the default browser.
        '''

        TIMEOUT = 120  # maximum number of seconds to wait before timeout

        for _ in range(TIMEOUT):
            if self._app_ready():
                self._open_new_tab()
                return

            time.sleep(1)

        print('WARNING: Webviz application still not ready after {TIMEOUT}s.'
              'Will not open browser automatically.')

    def _app_ready(self):
        '''Check if the flask instance is ready.
        '''

        no_proxy_env = os.environ.get('NO_PROXY')
        os.environ['NO_PROXY'] = 'localhost'

        try:
            with urllib.request.urlopen(f'http://localhost:{self._port}') \
                    as resp:
                response.read()
            app_ready = True
        except urllib.error.URLError as err:
            # The flask instance has not started
            app_ready = False
        except ConnectionResetError as err:
            # The flask instance has started but (correctly) abort
            # request due to "401 Unauthorized"
            app_ready = True
        finally:
            os.environ['NO_PROXY'] = no_proxy_env if no_proxy_env else ''

        return app_ready

    def _open_new_tab(self):
        '''Open the url (with token) in the default browser.
        '''

        print(' \n\033[92m'
              ' Opening the application in your default browser.\n'
              ' Press CTRL+C in this terminal window to stop the application.'
              ' \033[0m\n')

        webbrowser.open_new_tab(
            f'https://localhost:{self._port}?ott={self._token}'
        )
import os
import atexit
import pathlib
import shutil
import tempfile

from .._is_reload_process import is_reload_process
from ._certificate_generator import (
    create_certificate,
    SERVER_KEY_FILENAME,
    SERVER_CRT_FILENAME,
)


class LocalhostCertificate:
    """Facilitates creating certificates only valid for localhost, on the fly,
    when starting a local process. The certificates are stored in a temporary folder
    only readable by the user running the process, and are deleted on exit.
    """

    def __init__(self) -> None:
        if not is_reload_process():
            self._ssl_temp_dir = pathlib.Path(tempfile.mkdtemp())
            os.environ["WEBVIZ_SSL_TEMP_DIR"] = str(self._ssl_temp_dir)
            create_certificate(self._ssl_temp_dir)
            atexit.register(self._delete_temp_dir)
        else:
            self._ssl_temp_dir = pathlib.Path(os.environ["WEBVIZ_SSL_TEMP_DIR"])

    def _delete_temp_dir(self) -> None:
        """Delete temporary directory with on-the-fly generated localhost certificates"""
        shutil.rmtree(self._ssl_temp_dir)

    @property
    def ssl_context(self) -> tuple:
        return (
            self._ssl_temp_dir / SERVER_CRT_FILENAME,
            self._ssl_temp_dir / SERVER_KEY_FILENAME,
        )

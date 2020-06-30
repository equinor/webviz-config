import os
import socket
from typing import Optional


def get_available_port(preferred_port: Optional[int] = None) -> int:
    """Finds an available port for use in webviz on localhost. If a reload process,
    it will reuse the same port as found in the parent process by using an inherited
    environment variable.

    If preferred_port is given, ports in the range [preferred_port, preferred_port + 20)
    will be tried first, before an OS provided random port is used as fallback.
    """

    def is_available(port: int) -> bool:
        with socket.socket() as sock:
            try:
                sock.bind(("localhost", port))
                return True
            except OSError:
                return False

    if os.environ.get("WEBVIZ_PORT") is None:
        port = None

        if preferred_port is not None:
            for port_to_test in range(preferred_port, preferred_port + 20):
                if is_available(port_to_test):
                    port = port_to_test
                    break

        if port is None:
            with socket.socket() as sock:
                sock.bind(("localhost", 0))
                port = sock.getsockname()[1]

        os.environ["WEBVIZ_PORT"] = str(port)
        return port

    return int(os.environ.get("WEBVIZ_PORT"))  # type: ignore[arg-type]

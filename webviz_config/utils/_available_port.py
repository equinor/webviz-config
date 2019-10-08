import os
import socket


def get_available_port():
    """Finds an available port for use in webviz on localhost. If a reload process,
    it will reuse the same port as found in the parent process by using an inherited
    environment variable.
    """

    if os.environ.get("WEBVIZ_PORT") is None:
        sock = socket.socket()
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        sock.close()

        os.environ["WEBVIZ_PORT"] = str(port)
        return port

    return int(os.environ.get("WEBVIZ_PORT"))

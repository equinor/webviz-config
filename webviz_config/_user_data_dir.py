import sys
from pathlib import Path


def user_data_dir() -> Path:
    """Returns platform specific path to store user application data"""

    if sys.platform == "win32":
        return Path.home() / "Application Data" / "webviz"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "webviz"

    return Path.home() / ".local" / "share" / "webviz"

from enum import Enum
from pathlib import Path


class WebvizRunMode(Enum):
    NON_PORTABLE = 1
    PORTABLE = 2
    BUILDING_PORTABLE = 3


class WebvizInstanceInfo:
    """Class containing global info regarding the running webviz app instance"""

    def __init__(self, run_mode: WebvizRunMode, storage_folder: Path):
        self._run_mode = run_mode
        self._storage_folder = storage_folder

    @property
    def run_mode(self) -> WebvizRunMode:
        return self._run_mode

    @property
    def storage_folder(self) -> Path:
        return self._storage_folder

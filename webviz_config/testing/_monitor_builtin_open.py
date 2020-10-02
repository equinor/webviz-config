import io
import site
import inspect
import importlib
import warnings
from pathlib import Path

WHITELISTED_FILENAMES = ["geckodriver.log", ".pytest-sugar.conf"]
WHITELISTED_PREFIXES = ["/tmp"] + site.PREFIXES
WHITELISTED_POSTFIXES = [str(Path(".plotly" / Path(".config"))), ".py", ".json"]
WHITELISTED_CONTAINS = [
    ".pytest_cache",
    "__pycache__",
    ".cache",
    ".egg-info",
    "/dev/null",
]

import builtins

FUNCTIONS = [
    ("builtins", "open", "filepath"),
    ("pandas", "read_csv", "filepath"),
    ("xtgeo", "Well", "self"),
]


class MonitorBuiltinOpen:
    def __init__(self):
        self._original_functions = [
            getattr(importlib.import_module(module), function)
            for module, function, _ in FUNCTIONS
        ]

    def stop_monitoring(self):
        pass
        # builtins.open = self._original_open
        # io.open = self._original_open

    def start_monitoring(self):
        pass
        # def wrapped_open(*args, **kwargs):
        # path = str(args[0])
        # if Path(path).name not in WHITELISTED_FILENAMES and str(Path(path).parent) != "." and all([part not in path for part in WHITELISTED_CONTAINS]) and all([not path.startswith(prefix) for prefix in WHITELISTED_PREFIXES]) and all([not path.endswith(postfix) for postfix in WHITELISTED_POSTFIXES]):
        #    raise RuntimeError(f"File {path} opened, which is not white-listed as a 'portable' location.")
        # return self._original_open(*args, **kwargs)

        # builtins.open = wrapped_open
        # io.open = wrapped_open


monitor_builtin_open = MonitorBuiltinOpen()

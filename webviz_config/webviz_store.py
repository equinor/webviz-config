import os
import glob
import shutil
import functools
import hashlib
import inspect
import pathlib
from collections import defaultdict

import pandas as pd

from .utils import terminal_colors


class WebvizStorage:
    def __init__(self):
        self._use_storage = False
        self.storage_functions = set()
        self.storage_function_argvalues = defaultdict(dict)

    def register_function(self, func):
        """This function is automatically called by the function
        decorator @webvizstore, registering the function it decorates.
        """

        return_type = inspect.getfullargspec(func).annotations["return"]

        if return_type not in [pd.DataFrame, pathlib.Path]:
            raise NotImplementedError(
                "Currently only storage of dataframes "
                "and file resources are implemented."
            )

        self.storage_functions.add(func)

    @property
    def storage_folder(self):
        return self._storage_folder

    @storage_folder.setter
    def storage_folder(self, path):
        os.makedirs(path, exist_ok=True)
        self._storage_folder = path

    @property
    def use_storage(self):
        return self._use_storage

    @use_storage.setter
    def use_storage(self, use_storage):
        self._use_storage = use_storage

    def register_function_arguments(self, functionarguments):
        """The input here is from class functions `add_webvizstore(self)`
        in the different containers requested from the configuration file.

        The input is as follows:
            [(func1, argumentcombinations), (func2, argumentcombinations), ...]

        where argumentcombinations is a list of kwargs dictionaries.
        """

        for func, arglist in functionarguments:
            undec_func = WebvizStorage._undecorate(func)
            for args in arglist:
                argtuples = WebvizStorage._dict_to_tuples(
                    WebvizStorage.complete_kwargs(func, args)
                )
                if repr(argtuples) not in self.storage_function_argvalues[undec_func]:
                    self.storage_function_argvalues[undec_func][
                        repr(argtuples)
                    ] = argtuples

    def _unique_path(self, func, argtuples):
        """Encodes the argumenttuples as bytes, and then does a sha256 on that.
        Mutable arguments are accepted in the argument tuples, however it is
        the container author that needs to be repsonsible for making sure that
        instances representing different input has different values for
        `__repr__`
        """

        hashed_args = hashlib.sha256(repr(argtuples).encode()).hexdigest()

        filename = f"{func.__module__}-{func.__name__}-{hashed_args}"

        return os.path.join(self.storage_folder, filename)

    @staticmethod
    def _undecorate(func):
        """This unwraps potential multiple level of decorators, to get
        access to the original function.
        """

        while hasattr(func, "__wrapped__"):
            func = func.__wrapped__

        return func

    @staticmethod
    def string(func, kwargs):
        strkwargs = ", ".join([f"{k}={v!r}" for k, v in kwargs.items()])

        return f"{func.__name__}({strkwargs})"

    @staticmethod
    def _dict_to_tuples(dictionary):
        """Since dictionaries are not hashable, this is a helper function
        converting a dictionary into a sorted tuple."""

        return tuple(sorted(dictionary.items()))

    @staticmethod
    def complete_kwargs(func, kwargs):
        """This takes in a dictionary kwargs, and returns an updated
        dictionary where missing arguments are added with default values."""

        argspec = inspect.getfullargspec(func)

        if argspec.defaults is not None:
            ndef = len(argspec.defaults)
            for arg, val in zip(argspec.args[-ndef:], argspec.defaults):
                if arg not in kwargs:
                    kwargs[arg] = val

        return kwargs

    def get_stored_data(self, func, *args, **kwargs):

        argspec = inspect.getfullargspec(func)
        for arg_name, arg in zip(argspec.args, args):
            kwargs[arg_name] = arg

        WebvizStorage.complete_kwargs(func, kwargs)
        return_type = inspect.getfullargspec(func).annotations["return"]

        path = self._unique_path(func, WebvizStorage._dict_to_tuples(kwargs))

        try:
            if return_type == pd.DataFrame:
                return pd.read_parquet(f"{path}.parquet")
            if return_type == pathlib.Path:
                return pathlib.Path(glob.glob(f"{path}*")[0])
            raise ValueError(f"Unknown return type {return_type}")

        except OSError:
            raise OSError(
                f"Could not find file {path}, which should be the "
                "stored output of the function call "
                f"{WebvizStorage.string(func, kwargs)}."
            )

    def build_store(self):

        total_calls = sum(
            len(calls) for calls in self.storage_function_argvalues.values()
        )

        counter = 0
        for func in self.storage_functions:
            for argtuples in self.storage_function_argvalues[func].values():
                kwargs = dict(argtuples)

                print(
                    f"{terminal_colors.PURPLE}"
                    f" Running {WebvizStorage.string(func, kwargs)}"
                    f"{terminal_colors.END}",
                    end="",
                    flush=True,
                )

                output = func(**kwargs)
                path = self._unique_path(func, argtuples)

                if isinstance(output, pd.DataFrame):
                    output.to_parquet(f"{path}.parquet")
                elif isinstance(output, pathlib.Path):
                    shutil.copy(output, f"{path}{output.suffix}")
                else:
                    raise ValueError(f"Unknown return type {type(output)}")

                counter += 1
                print(
                    f"{terminal_colors.PURPLE}{terminal_colors.BOLD}"
                    f"[\u2713] Saved ({counter}/{total_calls})"
                    f"{terminal_colors.END}"
                )


def webvizstore(func):

    WEBVIZ_STORAGE.register_function(func)

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        if WEBVIZ_STORAGE.use_storage:
            return WEBVIZ_STORAGE.get_stored_data(func, *args, **kwargs)
        return func(*args, **kwargs)

    return wrapper_decorator


WEBVIZ_STORAGE = WebvizStorage()


@webvizstore
def get_resource(filename) -> pathlib.Path:
    """Utility funtion for getting a filename which works both for
    non-portable and portable webviz instances."""

    return pathlib.Path(filename)

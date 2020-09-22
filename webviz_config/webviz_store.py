import io
import glob
import shutil
import functools
import hashlib
import inspect
import pathlib
import warnings
from collections import defaultdict
from typing import Callable, List, Union, Any

import pandas as pd
from tqdm import tqdm


class WebvizStorage:

    RETURN_TYPES = [pd.DataFrame, pathlib.Path, io.BytesIO]

    def __init__(self) -> None:
        self._use_storage = False
        self.storage_functions: set = set()
        self.storage_function_argvalues: defaultdict = defaultdict(dict)

    def register_function(self, func: Callable) -> None:
        """This function is automatically called by the function
        decorator @webvizstore, registering the function it decorates.
        """
        return_type = inspect.getfullargspec(func).annotations["return"]

        if return_type not in WebvizStorage.RETURN_TYPES:
            raise NotImplementedError(
                f"Webviz storage type must be one of {WebvizStorage.RETURN_TYPES}"
            )

        self.storage_functions.add(func)

    @property
    def storage_folder(self) -> pathlib.Path:
        return self._storage_folder

    @storage_folder.setter
    def storage_folder(self, path: pathlib.Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self._storage_folder = path

    @property
    def use_storage(self) -> bool:
        return self._use_storage

    @use_storage.setter
    def use_storage(self, use_storage: bool) -> None:
        self._use_storage = use_storage

    def register_function_arguments(self, functionarguments: List[tuple]) -> None:
        """The input here is from class functions `add_webvizstore(self)`
        in the different plugins requested from the configuration file.

        The input is as follows:
            [(func1, argumentcombinations), (func2, argumentcombinations), ...]

        where argumentcombinations is a list of kwargs dictionaries.
        """

        for func, arglist in functionarguments:
            undec_func = WebvizStorage._undecorate(func)
            for args in arglist:
                argtuples = WebvizStorage._dict_to_tuples(
                    WebvizStorage.complete_kwargs(undec_func, args)
                )
                if repr(argtuples) not in self.storage_function_argvalues[undec_func]:
                    self.storage_function_argvalues[undec_func][
                        repr(argtuples)
                    ] = argtuples

                for (argname, argvalue) in argtuples:
                    # Check that values of decorated functions are not pandas objects.
                    # This function could probably at some point be moved into a pytest
                    # fixture (given that plugins use type hints) in order to slightly
                    # reduce running time.
                    if isinstance(argvalue, (pd.DataFrame, pd.Series)):
                        warnings.warn(
                            f"{func.__module__}.{func.__name__} is a @webvizstore decorated "
                            f"function, and argument {argname} has been given a pandas "
                            "object as value. Since pandas.DataFrames and pandas.Series are "
                            "known to not have unique/deterministic __repr__ functions, "
                            "they do not work well with @webvizstore (or flask-caching). "
                            "Consider moving to another object with a deterministic "
                            "__repr__ representation more suitable for hashing.",
                            RuntimeWarning,
                            stacklevel=0,
                        )

    def _unique_path(self, func: Callable, argtuples: tuple) -> str:
        """Encodes the argumenttuples as bytes, and then does a sha256 on that.
        Mutable arguments are accepted in the argument tuples, however it is
        the plugin author that needs to be responsible for making sure that
        instances representing different input has different values for
        `__repr__`
        """

        hashed_args = hashlib.sha256(repr(argtuples).encode()).hexdigest()

        filename = f"{func.__module__}-{func.__name__}-{hashed_args}"

        return str(self.storage_folder / filename)

    @staticmethod
    def _undecorate(func: Callable) -> Callable:
        """This unwraps potential multiple level of decorators, to get
        access to the original function.
        """

        while hasattr(func, "__wrapped__"):
            func = func.__wrapped__  # type: ignore[attr-defined]

        return func

    @staticmethod
    def string(func: Callable, kwargs: dict) -> str:
        strkwargs = ", ".join([f"{k}={v!r}" for k, v in kwargs.items()])

        return f"{func.__name__}({strkwargs})"

    @staticmethod
    def _dict_to_tuples(dictionary: dict) -> tuple:
        """Since dictionaries are not hashable, this is a helper function
        converting a dictionary into a sorted tuple."""

        return tuple(sorted(dictionary.items()))

    @staticmethod
    def complete_kwargs(func: Callable, kwargs: dict) -> dict:
        """This takes in a dictionary kwargs, and returns an updated
        dictionary where missing arguments are added with default values."""

        argspec = inspect.getfullargspec(func)

        if argspec.defaults is not None:
            ndef = len(argspec.defaults)
            for arg, val in zip(argspec.args[-ndef:], argspec.defaults):
                if arg not in kwargs:
                    kwargs[arg] = val

        return kwargs

    def get_stored_data(
        self, func: Callable, *args: Any, **kwargs: Any
    ) -> Union[pd.DataFrame, pathlib.Path, io.BytesIO]:

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
            if return_type == io.BytesIO:
                return io.BytesIO(pathlib.Path(path).read_bytes())
            raise ValueError(f"Unknown return type {return_type}")

        except OSError as exc:
            raise OSError(
                f"Could not find file {path}, which should be the "
                "stored output of the function call "
                f"{WebvizStorage.string(func, kwargs)}."
            ) from exc

    def build_store(self) -> None:

        total_calls = sum(
            len(calls) for calls in self.storage_function_argvalues.values()
        )

        with tqdm(
            total=total_calls, bar_format="{l_bar} {bar} | Saved {n_fmt}/{total_fmt}"
        ) as progress_bar:
            for func in self.storage_functions:
                if self.storage_function_argvalues[func]:
                    progress_bar.write(
                        f"Storing output of {func.__module__}.{func.__name__}"
                    )
                for argtuples in self.storage_function_argvalues[func].values():
                    output = func(**dict(argtuples))
                    path = self._unique_path(func, argtuples)

                    if isinstance(output, pd.DataFrame):
                        output.to_parquet(f"{path}.parquet")
                    elif isinstance(output, pathlib.Path):
                        shutil.copy(output, f"{path}{output.suffix}")
                    elif isinstance(output, io.BytesIO):
                        pathlib.Path(path).write_bytes(output.getvalue())
                    else:
                        raise ValueError(f"Unknown return type {type(output)}")

                    progress_bar.update()


def webvizstore(func: Callable) -> Callable:

    WEBVIZ_STORAGE.register_function(func)

    @functools.wraps(func)
    def wrapper_decorator(*args: Any, **kwargs: Any) -> Any:
        if WEBVIZ_STORAGE.use_storage:
            return WEBVIZ_STORAGE.get_stored_data(func, *args, **kwargs)
        return func(*args, **kwargs)

    return wrapper_decorator


WEBVIZ_STORAGE = WebvizStorage()


@webvizstore
def get_resource(filename: str) -> pathlib.Path:
    """Utility funtion for getting a filename which works both for
    non-portable and portable webviz instances."""

    return pathlib.Path(filename)

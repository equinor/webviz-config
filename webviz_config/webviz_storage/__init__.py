import io
import abc
import glob
import shutil
import functools
import hashlib
import inspect
import pathlib
import warnings
from collections import defaultdict
from typing import Callable, List, Union, Any, Type, Dict
import weakref

import numpy as np
import pandas as pd
from tqdm import tqdm


class ClassProperty:
    def __init__(self, fget: Callable):
        self.fget = fget

    def __get__(self, owner_self: Type[Any], owner_cls: Type[Any]) -> Any:
        print(type(owner_self), type(owner_cls))
        print(type(self.fget(owner_cls)))
        return self.fget(owner_cls)


class WebvizStorageType(abc.ABC):
    """ Base class for a webviz storage type """

    @staticmethod
    @abc.abstractmethod
    def get_data(path: str, **kwargs: Dict) -> None:
        """ Abstract method to retrieve stored data """

    @staticmethod
    @abc.abstractmethod
    def save_data(data: Any, path: str) -> Any:
        """ Abstract method to save data to store """


class WebvizStorageTypeRegistry:
    """ Registry of allowed webviz storage types """

    registry: Dict = {}

    @classmethod
    def register(cls, return_type: Type) -> Callable:
        def inner_wrapper(wrapped_class: Type) -> Type:
            if return_type in cls.registry:
                print(f"Storage type {return_type} already exists. Will replace it")
            cls.registry[return_type] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def create_storage_type(
        cls, return_type: str, **kwargs: Dict
    ) -> Union[None, WebvizStorageType]:
        """Factory command to create the storage type.
        This method gets the appropriate WebvizStorageType class from the registry
        and creates an instance of it, while passing in the parameters
        given in ``kwargs``.
        Args:
            return_type (str): The type of the storage type to create.
        Returns:
            An instance of the storage type that is created.
        """

        if return_type not in cls.registry:
            print(f"Storage type {return_type} does not exist in the registry")
            return None

        exec_class = cls.registry[return_type]
        return exec_class(**kwargs)

    # pylint: disable=no-self-argument
    @ClassProperty
    def return_types(cls) -> List:
        return list(cls.registry.keys())


@WebvizStorageTypeRegistry.register(pd.DataFrame)
class TypeDataFrame(WebvizStorageType):
    @staticmethod
    def get_data(path: str, **kwargs: Dict) -> Any:
        return pd.read_parquet(f"{path}.parquet")

    @staticmethod
    def save_data(data: Any, path: str) -> None:
        data.to_parquet(f"{path}.parquet")


@WebvizStorageTypeRegistry.register(pathlib.Path)
@WebvizStorageTypeRegistry.register(pathlib.PosixPath)
class TypePath(WebvizStorageType):
    @staticmethod
    def get_data(path: str, **kwargs: Dict) -> Any:
        return pathlib.Path(glob.glob(f"{path}*")[0])

    @staticmethod
    def save_data(data: Any, path: str) -> None:
        shutil.copy(data, f"{path}{data.suffix}")


@WebvizStorageTypeRegistry.register(list)
@WebvizStorageTypeRegistry.register(List)
class TypeList(WebvizStorageType):
    @staticmethod
    def get_data(path: str, **kwargs: Dict) -> Any:
        return np.load(f"{path}.npy").tolist()

    @staticmethod
    def save_data(data: Any, path: str) -> None:
        np.save(f"{path}.npy", data)


@WebvizStorageTypeRegistry.register(io.BytesIO)
class TypeBytesIO(WebvizStorageType):
    @staticmethod
    def get_data(path: str, **kwargs: Dict) -> Any:
        return np.load(f"{path}.npy").tolist()

    @staticmethod
    def save_data(data: Any, path: str) -> None:
        pathlib.Path(path).write_bytes(data.getvalue())

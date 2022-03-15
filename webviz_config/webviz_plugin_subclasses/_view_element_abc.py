from typing import Optional
import abc

from typing import Type, Union
from uuid import uuid4

from dash.development.base_component import Component


class ViewElementABC(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

        self._uuid: str = str(uuid4())

    def uuid(self, element: str) -> str:
        return f"{element}-{self._uuid}"

    def layout(self) -> Union[str, Type[Component]]:
        raise NotImplementedError

    def settings(self) -> Optional[Type[Component]]:
        return None

    def as_dict(self) -> dict:
        return {"id": self._uuid, "layout": self.layout(), "settings": self.settings()}

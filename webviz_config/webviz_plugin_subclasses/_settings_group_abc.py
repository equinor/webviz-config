from typing import Optional, Type
import abc

from uuid import uuid4

from dash.development.base_component import Component


class SettingsGroupABC(abc.ABC):
    def __init__(self, title: str) -> None:
        super().__init__()

        self.title = title
        self._uuid = str(uuid4())

    def uuid(self, element: Optional[str] = None) -> str:
        if element:
            return f"{element}-{self._uuid}"
        return self._uuid

    @property
    @abc.abstractmethod
    def layout(self) -> Type[Component]:
        raise NotImplementedError

    def as_dict(self) -> dict:
        return {"id": self._uuid, "title": self.title, "content": self.layout}

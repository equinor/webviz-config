from typing import List, Optional, overload


class LayoutUuid:
    def __init__(
        self,
        plugin_id: Optional[str] = None,
        view_id: Optional[str] = None,
        view_element_id: Optional[str] = None,
        settings_group_id: Optional[str] = None,
        component_id: Optional[str] = None,
        other: Optional["LayoutUuid"] = None,
    ) -> None:
        self._plugin_id = plugin_id
        self._view_id = view_id
        self._settings_group_id = settings_group_id
        self._view_element_id = view_element_id
        self._component_id = component_id

        if other:
            self.adopt(other)

    def get_plugin_id(self) -> Optional[str]:
        return self._plugin_id

    def get_view_uuid(self) -> str:
        ids: List[str] = []
        if self._plugin_id:
            ids.append(self._plugin_id)
        if self._view_id:
            ids.append(self._view_id)

        return "-".join(ids)

    def get_view_id(self) -> Optional[str]:
        return self._view_id

    def get_view_element_uuid(self) -> str:
        ids: List[str] = []
        if self._plugin_id:
            ids.append(self._plugin_id)
        if self._view_id:
            ids.append(self._view_id)
        if self._view_element_id:
            ids.append(self._view_element_id)

        return "-".join(ids)

    def get_view_element_id(self) -> Optional[str]:
        return self._view_element_id

    def get_component_id(self) -> Optional[str]:
        return self._component_id

    def get_settings_group_id(self) -> Optional[str]:
        return self._settings_group_id

    def set_plugin_id(self, plugin_id: str) -> None:
        self._plugin_id = plugin_id

    def set_view_id(self, view_id: str) -> None:
        self._view_id = view_id

    def set_view_element_id(self, view_element_id: str) -> None:
        self._view_element_id = view_element_id

    def set_settings_group_id(self, settings_group_id: str) -> None:
        self._settings_group_id = settings_group_id

    def set_component_id(self, component_id: str) -> None:
        self._component_id = component_id

    def is_plugin(self) -> bool:
        return (
            self._plugin_id != None
            and self._view_id == None
            and self.get_settings_group_id == None
        )

    def is_view(self) -> bool:
        return (
            self._view_id != None
            and self._view_element_id == None
            and self._settings_group_id == None
        )

    def is_view_element(self) -> bool:
        return self._view_element_id != None

    def is_settings_group(self) -> bool:
        return self._settings_group_id != None

    def is_component(self) -> bool:
        return self._component_id != None

    def adopt(self, other: "LayoutUuid") -> None:
        if self._plugin_id == None and other.get_plugin_id() != None:
            self._plugin_id = other.get_plugin_id()

        if self._view_id == None and other.get_view_id() != None:
            self._view_id = other.get_view_id()

        if self._view_element_id == None and other.get_view_element_id() != None:
            self._view_element_id = other.get_view_element_id()

        if self._settings_group_id == None and other.get_settings_group_id() != None:
            self._settings_group_id = other.get_settings_group_id()

        if self._component_id == None and other.get_component_id() != None:
            self._component_id = other.get_component_id()

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self) -> str:
        ids: List[str] = []
        if self._plugin_id:
            ids.append(self._plugin_id)
        if self._view_id:
            ids.append(self._view_id)
        if self._view_element_id:
            ids.append(self._view_element_id)
        if self._settings_group_id:
            ids.append(self._settings_group_id)
        if self._component_id:
            ids.append(self._component_id)

        return "-".join(ids)

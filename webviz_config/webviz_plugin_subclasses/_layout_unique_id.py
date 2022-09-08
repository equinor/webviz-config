from typing import List, Optional


class LayoutUniqueId:
    def __init__(
        self,
        plugin_uuid: Optional[str] = None,
        view_id: Optional[str] = None,
        view_element_id: Optional[str] = None,
        settings_group_id: Optional[str] = None,
        component_id: Optional[str] = None,
        other: Optional["LayoutUniqueId"] = None,
    ) -> None:
        self._plugin_uuid = plugin_uuid
        self._view_id = view_id
        self._settings_group_id = settings_group_id
        self._view_element_id = view_element_id
        self._component_id = component_id

        if other:
            self.adopt(other)

    def get_plugin_uuid(self) -> Optional[str]:
        return self._plugin_uuid

    def get_view_unique_id(self) -> str:
        ids: List[str] = []
        if not self._view_id:
            return ""

        if self._plugin_uuid:
            ids.append(self._plugin_uuid)
        if self._view_id:
            ids.append(self._view_id)

        return "-".join(ids)

    def get_view_id(self) -> Optional[str]:
        return self._view_id

    def get_view_element_unique_id(self) -> str:
        ids: List[str] = []
        if self._plugin_uuid:
            ids.append(self._plugin_uuid)
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

    def get_settings_group_unique_id(self) -> str:
        ids: List[str] = []
        if self._plugin_uuid:
            ids.append(self._plugin_uuid)
        if self._view_id:
            ids.append(self._view_id)
        if self._view_element_id:
            ids.append(self._view_element_id)
        if self._settings_group_id:
            ids.append(self._settings_group_id)

        return "-".join(ids)

    def set_plugin_uuid(self, plugin_uuid: str) -> None:
        self._plugin_uuid = plugin_uuid

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
            self._plugin_uuid is not None
            and self._view_id is None
            and self._settings_group_id is None
        )

    def is_view(self) -> bool:
        return (
            self._view_id is not None
            and self._view_element_id is None
            and self._settings_group_id is None
        )

    def is_view_element(self) -> bool:
        return self._view_element_id is not None

    def is_settings_group(self) -> bool:
        return self._settings_group_id is not None

    def is_component(self) -> bool:
        return self._component_id is not None

    def adopt(self, other: "LayoutUniqueId") -> None:
        if self._plugin_uuid is None and other.get_plugin_uuid() is not None:
            self._plugin_uuid = other.get_plugin_uuid()

        if self._view_id is None and other.get_view_id() is not None:
            self._view_id = other.get_view_id()

        if self._view_element_id is None and other.get_view_element_id() is not None:
            self._view_element_id = other.get_view_element_id()

        if (
            self._settings_group_id is None
            and other.get_settings_group_id() is not None
        ):
            self._settings_group_id = other.get_settings_group_id()

        if self._component_id is None and other.get_component_id() is not None:
            self._component_id = other.get_component_id()

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self) -> str:
        ids: List[str] = []
        if self._plugin_uuid:
            ids.append(self._plugin_uuid)
        if self._view_id:
            ids.append(self._view_id)
        if self._view_element_id:
            ids.append(self._view_element_id)
        if self._settings_group_id:
            ids.append(self._settings_group_id)
        if self._component_id:
            ids.append(self._component_id)

        return "-".join(ids)

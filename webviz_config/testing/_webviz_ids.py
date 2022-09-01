from enum import Enum


class WebvizIds(str, Enum):
    LAYOUT_WRAPPER = "layoutWrapper"
    CONTENT_MANAGER = "webviz-content-manager"
    SETTINGS_DRAWER = "settings-drawer"
    PLUGINS_WRAPPER = "plugins-wrapper"
    SETTINGS_DRAWER_TOGGLE_OPEN = ".WebvizSettingsDrawer__ToggleOpen"

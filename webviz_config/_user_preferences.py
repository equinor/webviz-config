import json
import webbrowser
from typing import Optional

from ._user_data_dir import user_data_dir
from .themes import installed_themes

USER_SETTINGS_FILE = user_data_dir() / "user_settings.json"


def set_user_preferences(
    theme: Optional[str] = None, browser: Optional[str] = None
) -> None:

    preferences = (
        json.loads(USER_SETTINGS_FILE.read_text())
        if USER_SETTINGS_FILE.is_file()
        else {}
    )

    new_preferences = {}

    if theme is not None:
        if theme not in installed_themes:
            raise ValueError(
                f"Theme {theme} is not one of the installed themes ({', '.join(installed_themes)})"
            )
        new_preferences["theme"] = theme

    if browser is not None:
        try:
            webbrowser.get(using=browser)
        except webbrowser.Error as exc:
            raise ValueError(
                f"Could not find an installed browser with the name {browser}."
            ) from exc

        new_preferences["browser"] = browser

    if new_preferences:
        preferences.update(new_preferences)
        USER_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        USER_SETTINGS_FILE.write_text(json.dumps(preferences))


def get_user_preference(setting: str) -> Optional[str]:
    return (
        json.loads(USER_SETTINGS_FILE.read_text()).get(setting)
        if USER_SETTINGS_FILE.is_file()
        else None
    )

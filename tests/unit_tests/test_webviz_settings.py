from typing import cast

import pytest

from webviz_config import WebvizConfigTheme, WebvizSettings


def test_construction_and_basic_access() -> None:
    # pylint: disable=unidiomatic-typecheck
    the_shared_settings = {"somenumber": 10, "somestring": "abc"}
    the_theme = WebvizConfigTheme("dummyThemeName")
    settings_obj = WebvizSettings(the_shared_settings, the_theme)

    copy_of_shared_settings = settings_obj.shared_settings
    assert copy_of_shared_settings is not the_shared_settings
    assert type(copy_of_shared_settings) == type(the_shared_settings)
    assert copy_of_shared_settings == the_shared_settings
    the_shared_settings["somestring"] = "MODIFIED"
    assert copy_of_shared_settings != the_shared_settings

    copy_of_theme = settings_obj.theme
    assert copy_of_theme is not the_theme
    assert type(copy_of_theme) == type(the_theme)
    assert copy_of_theme.__dict__ == the_theme.__dict__
    the_theme.theme_name = "MODIFIED"
    assert copy_of_theme.__dict__ != the_theme.__dict__


def test_construction_with_invalid_types() -> None:
    with pytest.raises(TypeError):
        theme = WebvizConfigTheme("dummyThemeName")
        _settings_obj = WebvizSettings(cast(dict, None), theme)

    with pytest.raises(TypeError):
        shared_settings = {"somenumber": 10, "somestring": "abc"}
        _settings_obj = WebvizSettings(shared_settings, cast(WebvizConfigTheme, None))

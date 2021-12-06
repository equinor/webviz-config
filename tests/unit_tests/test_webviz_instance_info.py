from pathlib import Path
from typing import cast

import pytest
from dash import Dash

from webviz_config import WebvizConfigTheme
from webviz_config.webviz_instance_info import WebvizInstanceInfo, WebvizRunMode


def test_construction_and_basic_access() -> None:
    my_dash_app = Dash("dummyAppName")
    my_run_mode = WebvizRunMode.NON_PORTABLE
    my_theme = WebvizConfigTheme("dummyThemeName")
    my_storage_folder = Path("dummyPath")

    instance_info = WebvizInstanceInfo()
    instance_info.initialize(
        dash_app=my_dash_app,
        run_mode=my_run_mode,
        theme=my_theme,
        storage_folder=my_storage_folder,
    )

    assert instance_info.dash_app is my_dash_app
    assert instance_info.run_mode is WebvizRunMode.NON_PORTABLE
    assert instance_info.theme.__dict__ == my_theme.__dict__
    assert instance_info.storage_folder == Path("dummyPath")


def test_that_construction_with_invalid_types_throw() -> None:
    dash_app = Dash("dummyAppName")
    run_mode = WebvizRunMode.NON_PORTABLE
    theme = WebvizConfigTheme("dummyThemeName")
    storage_folder = Path("dummyPath")

    with pytest.raises(TypeError):
        WebvizInstanceInfo().initialize(
            dash_app=cast(Dash, None),
            run_mode=run_mode,
            theme=theme,
            storage_folder=storage_folder,
        )
    with pytest.raises(TypeError):
        WebvizInstanceInfo().initialize(
            dash_app=dash_app,
            run_mode=cast(WebvizRunMode, None),
            theme=theme,
            storage_folder=storage_folder,
        )
    with pytest.raises(TypeError):
        WebvizInstanceInfo().initialize(
            dash_app=dash_app,
            run_mode=run_mode,
            theme=cast(WebvizConfigTheme, None),
            storage_folder=storage_folder,
        )
    with pytest.raises(TypeError):
        WebvizInstanceInfo().initialize(
            dash_app=dash_app,
            run_mode=run_mode,
            theme=theme,
            storage_folder=cast(Path, None),
        )


def test_immutability() -> None:
    my_dash_app = Dash("dummyAppName")
    my_run_mode = WebvizRunMode.NON_PORTABLE
    my_theme = WebvizConfigTheme("dummyThemeName")
    my_storage_folder = Path("dummyPath")

    instance_info = WebvizInstanceInfo()
    instance_info.initialize(
        dash_app=my_dash_app,
        run_mode=my_run_mode,
        theme=my_theme,
        storage_folder=my_storage_folder,
    )

    # Ony allowed to initialize once
    with pytest.raises(RuntimeError):
        instance_info.initialize(
            dash_app=my_dash_app,
            run_mode=my_run_mode,
            theme=my_theme,
            storage_folder=my_storage_folder,
        )

    # This is ok and necessary since we want to share the actual dash app
    assert instance_info.dash_app is my_dash_app

    # This two are also ok since integer enums and Path themselves is immutable
    assert instance_info.run_mode is my_run_mode
    assert instance_info.storage_folder is my_storage_folder

    returned_theme = instance_info.theme
    assert returned_theme is not my_theme
    assert isinstance(returned_theme, WebvizConfigTheme)
    assert returned_theme.__dict__ == my_theme.__dict__
    my_theme.theme_name = "MODIFIED"
    assert returned_theme.__dict__ != my_theme.__dict__

    with pytest.raises(AttributeError):
        # pylint: disable=assigning-non-slot
        instance_info.some_new_attribute = "myAttributeValue"  # type: ignore[attr-defined]

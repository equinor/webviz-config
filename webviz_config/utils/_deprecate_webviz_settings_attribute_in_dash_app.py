from typing import Any
import warnings

import dash


def _get_deprecated_webviz_settings(self: Any) -> dict:
    warnings.warn(
        "Accessing webviz_settings through the Dash application object has been deprecated, "
        "see https://github.com/equinor/webviz-config/pull/368",
        DeprecationWarning,
        stacklevel=2,
    )
    # pylint: disable=protected-access
    return self._deprecated_webviz_settings


def deprecate_webviz_settings_attribute_in_dash_app() -> None:
    """Helper that monkey patches dash.Dash application class so that access to
    the webviz_settings via the Dash application instance attribute is reported
    as being deprecated.
    """
    dash.Dash.webviz_settings = property(
        _get_deprecated_webviz_settings,
        None,
        None,
        "Property to mark webviz_settings access as deprecated",
    )

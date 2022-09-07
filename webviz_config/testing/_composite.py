from typing import Any

import pathlib

from dash.testing.composite import Browser
import dash
import webviz_core_components as wcc

from webviz_config.common_cache import CACHE
from webviz_config.themes import default_theme
from webviz_config.webviz_factory_registry import WEBVIZ_FACTORY_REGISTRY
from webviz_config.webviz_instance_info import WEBVIZ_INSTANCE_INFO, WebvizRunMode
from webviz_config import WebvizPluginABC

from ._webviz_ids import WebvizIds


class WebvizComposite(Browser):
    def __init__(self, server: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.app = dash.Dash(__name__)
        self.server = server
        self.plugin: WebvizPluginABC
        self.init_app()

    def init_app(self) -> None:
        WEBVIZ_INSTANCE_INFO.initialize(
            dash_app=self.app,
            run_mode=WebvizRunMode.NON_PORTABLE,
            theme=default_theme,
            storage_folder=pathlib.Path(__file__).resolve().parent,
        )
        try:
            WEBVIZ_FACTORY_REGISTRY.initialize(None)
        except RuntimeError:
            pass

        self.app.css.config.serve_locally = True
        self.app.scripts.config.serve_locally = True
        self.app.config.suppress_callback_exceptions = True
        CACHE.init_app(self.app.server)

    def start_server(self, plugin: WebvizPluginABC, **kwargs: Any) -> None:
        """Start the local server with app."""

        self.app.layout = dash.html.Div(
            className=WebvizIds.LAYOUT_WRAPPER,
            children=[
                wcc.WebvizContentManager(
                    id=WebvizIds.CONTENT_MANAGER,
                    children=[
                        wcc.WebvizSettingsDrawer(
                            id=WebvizIds.SETTINGS_DRAWER,
                            children=plugin.get_all_settings(),
                        ),
                        wcc.WebvizPluginsWrapper(
                            id=WebvizIds.PLUGINS_WRAPPER,
                            children=plugin.plugin_layout(),
                        ),
                    ],
                ),
            ],
        )
        self.plugin = plugin
        # start server with app and pass Dash arguments
        self.server(self.app, **kwargs)

        # set the default server_url, it implicitly call wait_for_page
        self.server_url = self.server.url

    def toggle_webviz_settings_drawer(self) -> None:
        """Open the plugin settings drawer"""
        self.wait_for_element(WebvizIds.SETTINGS_DRAWER_TOGGLE_OPEN).click()

    def toggle_webviz_settings_group(self, settings_group_id: str) -> None:
        """Open the respective settings group in the settings drawer"""
        self.wait_for_element(
            f"#{settings_group_id} > .WebvizSettingsGroup__Title"
        ).click()

    def shared_settings_group_unique_component_id(
        self, settings_group_id: str, component_unique_id: str
    ) -> str:
        """Returns the element id of a component in a shared settings group"""
        unique_id = (
            self.plugin.shared_settings_group(settings_group_id)
            .component_unique_id(component_unique_id)
            .to_string()
        )
        return f"#{unique_id}"

    def view_settings_group_unique_component_id(
        self, view_id: str, settings_group_id: str, component_unique_id: str
    ) -> str:
        """Returns the element id of a component in a view settings group"""
        unique_id = (
            self.plugin.view(view_id)
            .settings_group(settings_group_id)
            .component_unique_id(component_unique_id)
            .to_string()
        )
        return f"#{unique_id}"

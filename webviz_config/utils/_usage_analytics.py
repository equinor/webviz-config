import logging
import os
import platform
import pwd
from importlib.metadata import version

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource

_APP_INSIGHTS_CONN_STRING = None


class UsageAnalytics:
    def __init__(self, telemetry_logger: logging.Logger, user_name: str | None) -> None:
        self._telemetry_logger = telemetry_logger
        self._user_name = user_name

    def log_plugin_usage(self, path_name: str, plugin_name: str) -> None:
        log_msg = f"PLUGIN_USAGE - plugin_name={plugin_name}, user_name={self._user_name}, path_name={path_name}"
        print(f"log_plugin_usage(): {log_msg}")

        extra = {
            "wv_plugin_name": plugin_name,
            "wv_user_name": self._user_name,
            "wv_path_name": path_name,
        }

        self._telemetry_logger.info(log_msg, extra=extra)


def setup_usage_analytics() -> UsageAnalytics | None:
    # We only want these analytics when running on-prem, so silently skip the setup if we detect that we are running on the Radix platform.
    is_on_radix_platform = bool(os.getenv("RADIX_APP") and os.getenv("RADIX_ENVIRONMENT"))
    if is_on_radix_platform:
        return None

    if _APP_INSIGHTS_CONN_STRING is None:
        print("Skipping setup of telemetry for usage analytics, no connection string provided.")
        return None

    print("Setting up telemetry for usage analytics...")

    wv_config_pkg_version = version("webviz-config")
    username = _get_username()
    hostname = _get_hostname()

    try:
        configure_azure_monitor(
            connection_string=_APP_INSIGHTS_CONN_STRING,
            logger_name="wv_telemetry_logger",
            sampling_ratio=1.0,
            resource=Resource.create(
                attributes={
                    "service.name": "WebvizDash",
                    "service.namespace": hostname,
                    "service.version": wv_config_pkg_version,
                }
            ),
            enable_live_metrics=False,
            enable_performance_counters=False,
            # For now, drop the actual flask instrumentation as it doesn't add much value
            instrumentation_options={"flask": {"enabled": False}},
        )
    except Exception as e:
        print(f"Failed to set up telemetry for usage analytics, proceeding without telemetry. Error: {e}")
        return None

    telemetry_logger = logging.getLogger("wv_telemetry_logger")
    telemetry_logger.setLevel(logging.INFO)

    # Don't propagate telemetry logs to the root logger, since that would cause them to be
    # printed to console by the default logging configuration.
    telemetry_logger.propagate = False

    return UsageAnalytics(telemetry_logger=telemetry_logger, user_name=username)


def _get_hostname() -> str:
    hostname =  platform.node()
    if hostname is None or hostname == "":
        print("Failed to get hostname, defaulting to 'unknown_host'.")
        return "unknown_host"

    return hostname


def _get_username() -> str:
    try:
        uid = os.getuid()
        return pwd.getpwuid(uid).pw_name
    except Exception as e:
        print(f"Failed to get username, defaulting to 'unknown_user'. Error: {e}")
        return "unknown_user"

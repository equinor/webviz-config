import logging
import os
import platform
import pwd
from importlib.metadata import entry_points, version
from typing import Optional

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource

# pylint: disable=line-too-long

_LOGGING_CONN_STRING_ENTRYPOINT_GROUP = "webviz"
_LOGGING_CONN_STRING_ENTRYPOINT_NAME = "webviz-azure-logging-connection-string"


class UsageAnalytics:
    def __init__(self, telemetry_logger: logging.Logger, user_name: str) -> None:
        self._telemetry_logger = telemetry_logger
        self._user_name = user_name

    def log_plugin_usage(self, path_name: str, plugin_name: str) -> None:
        log_msg = f"PLUGIN_USAGE - plugin_name={plugin_name}, user_name={self._user_name}, path_name={path_name}"
        # print(f"log_plugin_usage(): {log_msg}")

        extra = {
            "wv_plugin_name": plugin_name,
            "wv_user_name": self._user_name,
            "wv_path_name": path_name,
        }

        self._telemetry_logger.info(log_msg, extra=extra)


def setup_usage_analytics() -> Optional[UsageAnalytics]:
    app_insights_connection_string = _get_connection_string_from_entrypoint()
    if app_insights_connection_string is None:
        return None

    print("")
    print("Setting up telemetry for usage analytics...")
    print("")
    print(
        "We encourage you to implement the new version of Webviz (https://webviz.fmu.equinor.com) that uses Sumo (https://sumo.fmu.equinor.com) as its data source. "
        "Please let us know if you are blocked from transitioning to this new cloud-only setup."
    )
    print("")
    print(
        "To support the transition, usage of on-prem Webviz is logged centrally. "
        "This allows us to monitor remaining on-prem activity and proactively support users in transitioning. No underlying project data will be collected."
    )
    print("")

    wv_config_pkg_version = version("webviz-config")
    username = _get_username()
    hostname = _get_hostname()

    try:
        configure_azure_monitor(
            connection_string=app_insights_connection_string,
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
    except Exception as exc:  # pylint: disable=broad-except
        print(
            f"Failed to set up telemetry for usage analytics, proceeding without telemetry. Error: {exc}"
        )
        return None

    telemetry_logger = logging.getLogger("wv_telemetry_logger")
    telemetry_logger.setLevel(logging.INFO)

    # Don't propagate telemetry logs to the root logger, since that would cause them to be
    # printed to console by the default logging configuration.
    telemetry_logger.propagate = False

    return UsageAnalytics(telemetry_logger=telemetry_logger, user_name=username)


def _get_connection_string_from_entrypoint() -> Optional[str]:
    try:
        matching_entry_points = entry_points(
            group=_LOGGING_CONN_STRING_ENTRYPOINT_GROUP,
            name=_LOGGING_CONN_STRING_ENTRYPOINT_NAME,
        )
    except Exception as exc:  # pylint: disable=broad-except
        print(
            "Failed to inspect entry points for usage analytics connection string, "
            f"proceeding without telemetry. Error: {exc}"
        )
        return None

    if not matching_entry_points:
        return None

    try:
        connection_string = next(iter(matching_entry_points)).load()
    except Exception as exc:  # pylint: disable=broad-except
        print(
            "Failed to load usage analytics connection string from entry point, "
            f"proceeding without telemetry. Error: {exc}"
        )
        return None

    if not isinstance(connection_string, str) or connection_string.strip() == "":
        print(
            "Usage analytics connection string entry point was found, but did not "
            "resolve to a non-empty string. Proceeding without telemetry."
        )
        return None

    return connection_string


def _get_hostname() -> str:
    hostname = platform.node()
    if hostname is None or hostname == "":
        print("Failed to get hostname, defaulting to 'unknown_host'.")
        return "unknown_host"

    return hostname


def _get_username() -> str:
    try:
        uid = os.getuid()
        return pwd.getpwuid(uid).pw_name
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to get username, defaulting to 'unknown_user'. Error: {exc}")
        return "unknown_user"

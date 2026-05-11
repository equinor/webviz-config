import atexit
import os
import platform
import pwd
from importlib.metadata import entry_points, version
from typing import Optional

from azure.monitor.events.extension import track_event
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk.resources import Resource

# opentelemetry.sdk._logs is experimental, but official Microsoft package
# azure-monitor-opentelemetry depends on them as well (a package we don't want
# to use due to larger unncessary dependency tree in Komodo)
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


# pylint: disable=line-too-long

_LOGGING_CONN_STRING_ENTRYPOINT_GROUP = "webviz"
_LOGGING_CONN_STRING_ENTRYPOINT_NAME = "webviz-azure-logging-connection-string"


class UsageAnalytics:
    def __init__(self, user_name: str) -> None:
        self._user_name = user_name

    def log_plugin_usage(self, path_name: str, plugin_name: str) -> None:
        track_event(
            "PLUGIN_USAGE",
            {
                "wv_plugin_name": plugin_name,
                "wv_user_name": self._user_name,
                "wv_path_name": path_name,
            },
        )


def setup_usage_analytics() -> Optional[UsageAnalytics]:
    # Env var can be set to opt out of all telemetry
    if _get_bool_env("WEBVIZ_DISABLE_USAGE_ANALYTICS"):
        print(
            "Usage analytics is disabled via environment variable, skipping setup of telemetry for usage analytics."
        )
        return None

    # Allow specification of AppInsights connection string through env var for troubleshooting and local development purposes
    if os.getenv("WEBVIZ_APP_INSIGHTS_CONN_STRING") is not None:
        app_insights_connection_string = os.getenv("WEBVIZ_APP_INSIGHTS_CONN_STRING")
        print("Usage analytics connection string set via environment variable.")
    else:
        # This is the mainstream and intended way to specify the AppInsights connection string
        app_insights_connection_string = _get_connection_string_from_entrypoint()

    if app_insights_connection_string is None:
        return None

    print("")
    print("Setting up telemetry for usage analytics...")
    print("")
    print(
        "We encourage you to implement the new version of Webviz (https://webviz.fmu.equinor.com) that uses Sumo (https://sumo.fmu.equinor.com) as its data source.\n"
        "Please let us know if you are blocked from transitioning to this new cloud-only setup."
    )
    print("")
    print(
        "To support the transition, usage of on-prem Webviz is logged centrally.\n"
        "This allows us to monitor remaining on-prem activity and proactively support users in transitioning.\n"
        "No underlying project data will be collected."
    )
    print("")

    wv_config_pkg_version = version("webviz-config")
    username = _get_username()
    hostname = _get_hostname()

    try:
        resource = Resource.create(
            attributes={
                "service.name": "WebvizDash",
                "service.namespace": hostname,
                "service.version": wv_config_pkg_version,
            }
        )

        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(
                AzureMonitorLogExporter(
                    connection_string=app_insights_connection_string
                )
            )
        )
        set_logger_provider(logger_provider)

        # Ensure buffered log records are flushed before interpreter exit.
        atexit.register(logger_provider.shutdown)
    except Exception as exc:  # pylint: disable=broad-except
        print(
            f"Failed to set up telemetry for usage analytics, proceeding without telemetry. Error: {exc}"
        )
        return None

    return UsageAnalytics(user_name=username)


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


def _get_bool_env(name: str) -> bool:
    value = os.getenv(name)
    if value is None:
        return False

    return value.strip().lower() in {"1", "true", "yes", "on"}

import logging
import os
import platform
import pwd
from importlib.metadata import version
from typing import Optional

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource

# pylint: disable=line-too-long

_APP_INSIGHTS_CONN_STRING = "InstrumentationKey=c3c73643-624c-40e5-9fd0-64cf0fcfb004;IngestionEndpoint=https://norwayeast-0.in.applicationinsights.azure.com/;LiveEndpoint=https://norwayeast.livediagnostics.monitor.azure.com/;ApplicationId=fa7bdafc-620b-4182-8b8c-9c1a11c738ba"


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
    # We only want these analytics when running on-prem inside Equinor, so rely on KOMODO_RELEASE env var to enable analytics.
    is_komodo_definedon = bool(os.getenv("KOMODO_RELEASE"))
    if not is_komodo_definedon:
        return None

    if _get_bool_env("WEBVIZ_DISABLE_USAGE_ANALYTICS"):
        print(
            "Usage analytics is disabled via environment variable, skipping setup of telemetry for usage analytics."
        )
        return None

    print("")
    print("Setting up telemetry for usage analytics...")
    print("")
    print(
        "We encourage you to implement the new version of Webviz (https://webviz.fmu.equinor.com) that uses Sumo (https://sumo.fmu.equinor.com) as its data source."
        "Please let us know if you are blocked from transitioning to this new cloud-only setup."
    )
    print("")
    print(
        "To support the transition, usage of on-prem Webviz will now be logged by default in all FMU workflows, i.e. where KOMODO_RELEASE is defined."
        "This allows us to monitor remaining on-prem activity and proactively support users in transitioning. No underlying project data will be collected."
        "To opt out of this logging, set the environment variable WEBVIZ_DISABLE_USAGE_ANALYTICS=1."
    )
    print("")

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

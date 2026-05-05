import logging
from dataclasses import dataclass

from webviz_config.utils import _usage_analytics


@dataclass
class _DummyEntryPoint:
    loaded_value: object

    def load(self) -> object:
        return self.loaded_value


def test_setup_usage_analytics_returns_none_without_entrypoint(
    monkeypatch,
) -> None:
    configure_calls = []

    monkeypatch.setattr(
        _usage_analytics,
        "_get_connection_string_from_entrypoint",
        lambda: None,
    )
    monkeypatch.setattr(
        _usage_analytics,
        "configure_azure_monitor",
        lambda **kwargs: configure_calls.append(kwargs),
    )

    usage_analytics = _usage_analytics.setup_usage_analytics()

    assert usage_analytics is None
    assert not configure_calls


def test_setup_usage_analytics_configures_telemetry_when_entrypoint_exists(
    monkeypatch,
) -> None:
    configure_calls = []

    monkeypatch.setattr(
        _usage_analytics,
        "_get_connection_string_from_entrypoint",
        lambda: "Endpoint=sb://example/;InstrumentationKey=abc",
    )
    monkeypatch.setattr(
        _usage_analytics,
        "version",
        lambda _package_name: "9.9.9",
    )
    monkeypatch.setattr(_usage_analytics, "_get_username", lambda: "test-user")
    monkeypatch.setattr(_usage_analytics, "_get_hostname", lambda: "test-host")
    monkeypatch.setattr(
        _usage_analytics,
        "configure_azure_monitor",
        lambda **kwargs: configure_calls.append(kwargs),
    )

    usage_analytics = _usage_analytics.setup_usage_analytics()

    assert isinstance(usage_analytics, _usage_analytics.UsageAnalytics)
    assert usage_analytics._user_name == "test-user"
    assert usage_analytics._telemetry_logger is logging.getLogger("wv_telemetry_logger")
    assert len(configure_calls) == 1
    assert (
        configure_calls[0]["connection_string"]
        == "Endpoint=sb://example/;InstrumentationKey=abc"
    )


def test_get_connection_string_from_entrypoint_returns_none_when_missing(
    monkeypatch,
) -> None:
    monkeypatch.setattr(_usage_analytics, "entry_points", lambda **_kwargs: [])

    assert _usage_analytics._get_connection_string_from_entrypoint() is None


def test_get_connection_string_from_entrypoint_loads_string(monkeypatch) -> None:
    monkeypatch.setattr(
        _usage_analytics,
        "entry_points",
        lambda **_kwargs: [_DummyEntryPoint("conn-str")],
    )

    assert _usage_analytics._get_connection_string_from_entrypoint() == "conn-str"


def test_get_connection_string_from_entrypoint_rejects_non_string(monkeypatch) -> None:
    monkeypatch.setattr(
        _usage_analytics,
        "entry_points",
        lambda **_kwargs: [_DummyEntryPoint(123)],
    )

    assert _usage_analytics._get_connection_string_from_entrypoint() is None

from prometheus_client.exposition import generate_latest
import pytest

from .opentelemetry import OpenTelemetryTracker
from .prometheus import PrometheusTracker

from .tracker import default_tracker, create_tracker, TrackerType

tracker_types = [TrackerType.PROMETHEUS, TrackerType.OPENTELEMETRY]


def test_default_tracker(monkeypatch):
    """Test the default tracker type."""

    monkeypatch.delenv("AUTOMETRICS_TRACKER", raising=False)
    tracker = default_tracker()
    assert isinstance(tracker, OpenTelemetryTracker)

    monkeypatch.setenv("AUTOMETRICS_TRACKER", "prometheus")
    tracker = default_tracker()
    assert isinstance(tracker, PrometheusTracker)
    monkeypatch.setenv("AUTOMETRICS_TRACKER", "PROMETHEUS")
    tracker = default_tracker()
    assert isinstance(tracker, PrometheusTracker)

    # Should use open telemetry when the tracker is not recognized
    monkeypatch.setenv("AUTOMETRICS_TRACKER", "something_else")
    tracker = default_tracker()
    assert isinstance(tracker, OpenTelemetryTracker)


def test_create_prometheus_tracker_set_build_info(monkeypatch):
    """Test that create_tracker calls set_build_info using env vars."""

    commit = "d6abce3"
    version = "1.0.1"

    monkeypatch.setenv("AUTOMETRICS_COMMIT", commit)
    monkeypatch.setenv("AUTOMETRICS_VERSION", version)

    prom_tracker = create_tracker(TrackerType.PROMETHEUS)
    assert isinstance(prom_tracker, PrometheusTracker)

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")

    prom_build_info = f"""build_info{{commit="{commit}",version="{version}"}} 1.0"""
    assert prom_build_info in data

    monkeypatch.delenv("AUTOMETRICS_VERSION", raising=False)
    monkeypatch.delenv("AUTOMETRICS_COMMIT", raising=False)


def test_create_otel_tracker_set_build_info(monkeypatch):
    """Test that create_tracker calls set_build_info using env vars."""

    pytest.skip("Skipping test because I am unser how to inspect otel metrics")

    commit = "a29a178"
    version = "0.0.1"

    monkeypatch.setenv("AUTOMETRICS_COMMIT", commit)
    monkeypatch.setenv("AUTOMETRICS_VERSION", version)

    # FIXME - Creating this again (after having created it in test_default_tracker) logs a warning, since you're not suppose to ever re-set the MeterProvider in the Otel tracker
    otel_tracker = create_tracker(TrackerType.OPENTELEMETRY)
    assert isinstance(otel_tracker, OpenTelemetryTracker)

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")

    prom_build_info = f"""build_info{{commit="{commit}",version="{version}"}} 1.0"""
    assert prom_build_info in data

    monkeypatch.delenv("AUTOMETRICS_VERSION", raising=False)
    monkeypatch.delenv("AUTOMETRICS_COMMIT", raising=False)


# def test_create_tracker_set_build_info_empty(monkeypatch):
#     """Test that create_tracker calls set_build_info with empty strings when none is present."""

#     monkeypatch.delenv("AUTOMETRICS_VERSION", raising=False)
#     monkeypatch.delenv("AUTOMETRICS_COMMIT", raising=False)

#     otel_tracker = create_tracker(TrackerType.OPENTELEMETRY)
#     assert isinstance(otel_tracker, OpenTelemetryTracker)

#     prom_tracker = create_tracker()
#     assert isinstance(prom_tracker, PrometheusTracker)

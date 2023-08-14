from prometheus_client.exposition import generate_latest
import pytest

from .opentelemetry import OpenTelemetryTracker
from .prometheus import PrometheusTracker

from .tracker import get_tracker, default_tracker

from .. import init


def test_default_tracker(monkeypatch):
    """Test the default tracker type."""

    monkeypatch.delenv("AUTOMETRICS_TRACKER", raising=False)
    init()
    tracker = default_tracker()
    assert isinstance(tracker, OpenTelemetryTracker)

    monkeypatch.setenv("AUTOMETRICS_TRACKER", "prometheus")
    init()
    tracker = default_tracker()
    assert isinstance(tracker, PrometheusTracker)
    monkeypatch.setenv("AUTOMETRICS_TRACKER", "PROMETHEUS")
    init()
    tracker = default_tracker()
    assert isinstance(tracker, PrometheusTracker)

    # Should use open telemetry when the tracker is not recognized
    monkeypatch.setenv("AUTOMETRICS_TRACKER", "something_else")
    init()
    tracker = default_tracker()
    assert isinstance(tracker, OpenTelemetryTracker)


def test_init_prometheus_tracker_set_build_info(monkeypatch):
    """Test that init_tracker (for a Prometheus tracker) calls set_build_info using env vars."""

    commit = "d6abce3"
    version = "1.0.1"
    branch = "main"
    tracker = "prometheus"

    monkeypatch.setenv("AUTOMETRICS_COMMIT", commit)
    monkeypatch.setenv("AUTOMETRICS_VERSION", version)
    monkeypatch.setenv("AUTOMETRICS_BRANCH", branch)
    monkeypatch.setenv("AUTOMETRICS_TRACKER", tracker)
    init()

    prom_tracker = get_tracker()
    assert isinstance(prom_tracker, PrometheusTracker)

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")
    print(data)

    prom_build_info = f"""build_info{{branch="{branch}",commit="{commit}",service_name="autometrics",version="{version}"}} 1.0"""
    assert prom_build_info in data

    monkeypatch.delenv("AUTOMETRICS_VERSION", raising=False)
    monkeypatch.delenv("AUTOMETRICS_COMMIT", raising=False)
    monkeypatch.delenv("AUTOMETRICS_BRANCH", raising=False)


def test_init_otel_tracker_set_build_info(monkeypatch):
    """
    Test that init_tracker (for an OTEL tracker) calls set_build_info using env vars.
    Note that the OTEL collector translates metrics to Prometheus.
    """
    pytest.skip(
        "Skipping test because OTEL collector does not create a gauge when it translates UpDownCounter to Prometheus"
    )

    commit = "a29a178"
    version = "0.0.1"
    branch = "main"

    monkeypatch.setenv("AUTOMETRICS_COMMIT", commit)
    monkeypatch.setenv("AUTOMETRICS_VERSION", version)
    monkeypatch.setenv("AUTOMETRICS_BRANCH", branch)
    init()

    otel_tracker = get_tracker()
    assert isinstance(otel_tracker, OpenTelemetryTracker)

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")

    prom_build_info = f"""build_info{{branch="{branch}",commit="{commit}",service_name="autometrics",version="{version}",service_name="autometrics"}} 1.0"""
    assert prom_build_info in data

    monkeypatch.delenv("AUTOMETRICS_VERSION", raising=False)
    monkeypatch.delenv("AUTOMETRICS_COMMIT", raising=False)
    monkeypatch.delenv("AUTOMETRICS_BRANCH", raising=False)

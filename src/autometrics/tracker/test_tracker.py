import pytest

from prometheus_client.exposition import generate_latest

from .opentelemetry import OpenTelemetryTracker
from .prometheus import PrometheusTracker
from .tracker import get_tracker

from ..initialization import init


@pytest.fixture(
    params=[
        (None, OpenTelemetryTracker),
        ("prometheus", PrometheusTracker),
        ("PROMETHEUS", PrometheusTracker),
        ("something_else", OpenTelemetryTracker),
    ]
)
def tracker_var(request):
    return request.param


def test_default_tracker(monkeypatch, tracker_var):
    """Test that the default tracker is set correctly."""
    (env_value, Tracker) = tracker_var
    if env_value is not None:
        monkeypatch.setenv("AUTOMETRICS_TRACKER", env_value)
    else:
        monkeypatch.delenv("AUTOMETRICS_TRACKER", raising=False)
    init()
    tracker = get_tracker()
    assert isinstance(tracker, Tracker)


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

    prom_build_info = f"""build_info{{autometrics_version="1.0.0",branch="{branch}",commit="{commit}",repository_provider="github",repository_url="git@github.com:autometrics-dev/autometrics-py.git",service_name="autometrics",version="{version}"}} 1.0"""
    assert prom_build_info in data

    monkeypatch.delenv("AUTOMETRICS_VERSION", raising=False)
    monkeypatch.delenv("AUTOMETRICS_COMMIT", raising=False)
    monkeypatch.delenv("AUTOMETRICS_BRANCH", raising=False)
    monkeypatch.delenv("AUTOMETRICS_TRACKER", raising=False)


def test_init_otel_tracker_set_build_info(monkeypatch):
    """
    Test that init_tracker (for an OTEL tracker) calls set_build_info using env vars.
    Note that the OTEL collector translates metrics to Prometheus.
    """

    commit = "a29a178"
    version = "0.0.1"
    branch = "main"
    tracker = "opentelemetry"

    monkeypatch.setenv("AUTOMETRICS_COMMIT", commit)
    monkeypatch.setenv("AUTOMETRICS_VERSION", version)
    monkeypatch.setenv("AUTOMETRICS_BRANCH", branch)
    monkeypatch.setenv("AUTOMETRICS_TRACKER", tracker)
    init()

    otel_tracker = get_tracker()
    assert isinstance(otel_tracker, OpenTelemetryTracker)

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")

    otel_build_info = f"""build_info{{autometrics_version="1.0.0",branch="{branch}",commit="{commit}",repository_provider="github",repository_url="git@github.com:autometrics-dev/autometrics-py.git",service_name="autometrics",version="{version}"}} 1.0"""
    assert otel_build_info in data

    monkeypatch.delenv("AUTOMETRICS_VERSION", raising=False)
    monkeypatch.delenv("AUTOMETRICS_COMMIT", raising=False)
    monkeypatch.delenv("AUTOMETRICS_BRANCH", raising=False)
    monkeypatch.delenv("AUTOMETRICS_TRACKER", raising=False)

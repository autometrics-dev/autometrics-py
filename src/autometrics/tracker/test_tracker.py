from .opentelemetry import OpenTelemetryTracker
from .prometheus import PrometheusTracker

from .tracker import default_tracker


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

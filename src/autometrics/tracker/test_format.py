from prometheus_client.exposition import generate_latest
import pytest

from . import init_tracker, TrackerType
from .opentelemetry import OpenTelemetryTracker
from ..decorator import autometrics


@pytest.mark.parametrize("tracker", TrackerType)
def test_metrics_format(tracker):
    """Test that the metrics are formatted correctly."""
    init_tracker(tracker)

    @autometrics
    def test_function():
        pass

    test_function()

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")

    assert "function_calls_total{" in data
    assert "function_calls_duration_seconds_bucket{" in data

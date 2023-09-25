from prometheus_client.exposition import generate_latest
import pytest

from . import TrackerType
from ..decorator import autometrics
from ..initialization import init


@pytest.mark.parametrize("tracker", TrackerType)
def test_metrics_format(tracker):
    """Test that the metrics are formatted correctly."""
    init(tracker=tracker.value, version="1.0")

    @autometrics
    def test_function():
        pass

    test_function()

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")

    assert "function_calls_total{" in data
    assert "function_calls_duration_seconds_bucket{" in data

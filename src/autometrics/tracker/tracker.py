from typing import Protocol, Optional
from enum import Enum
import os


from ..objectives import Objective


class Result(Enum):
    """Result of the function call."""

    OK = "ok"
    ERROR = "error"


class TrackMetrics(Protocol):
    """Protocol for tracking metrics."""

    def finish(
        self,
        start_time: float,
        function: str,
        module: str,
        caller: str,
        result: Result = Result.OK,
        objective: Optional[Objective] = None,
    ):
        """Finish tracking metrics for a function call."""


class TrackerType(Enum):
    """Type of tracker."""

    OPENTELEMETRY = "opentelemetry"
    PROMETHEUS = "prometheus"


def create_tracker(tracker_type: TrackerType) -> TrackMetrics:
    """Create a tracker"""
    if tracker_type == TrackerType.OPENTELEMETRY:
        # pylint: disable=import-outside-toplevel
        from .opentelemetry import OpenTelemetryTracker

        return OpenTelemetryTracker()
    elif tracker_type == TrackerType.PROMETHEUS:
        # pylint: disable=import-outside-toplevel
        from .prometheus import PrometheusTracker

        return PrometheusTracker()


def get_tracker_type() -> TrackerType:
    """Get the tracker type."""
    tracker_type = os.getenv("AUTOMETRICS_TRACKER") or "opentelemetry"
    if tracker_type.lower() == "prometheus":
        return TrackerType.PROMETHEUS
    return TrackerType.OPENTELEMETRY


def default_tracker():
    """Setup the default tracker."""
    preferred_tracker = get_tracker_type()
    return create_tracker(preferred_tracker)


tracker: TrackMetrics = default_tracker()


def get_tracker() -> TrackMetrics:
    """Get the tracker type."""
    return tracker


def set_tracker(tracker_type: TrackerType):
    """Set the tracker type."""
    global tracker
    tracker = create_tracker(tracker_type)

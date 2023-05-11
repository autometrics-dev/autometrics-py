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

    def set_build_info(self, commit: str, version: str):
        """Observe the build info. Should only be called once per tracker instance"""

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


def init_tracker(tracker_type: TrackerType) -> TrackMetrics:
    """Create a tracker"""
    tracker_instance = None
    if tracker_type == TrackerType.OPENTELEMETRY:
        # pylint: disable=import-outside-toplevel
        from .opentelemetry import OpenTelemetryTracker

        tracker_instance = OpenTelemetryTracker()
    elif tracker_type == TrackerType.PROMETHEUS:
        # pylint: disable=import-outside-toplevel
        from .prometheus import PrometheusTracker

        tracker_instance = PrometheusTracker()

    # NOTE - Only set the build info when the tracker is initialized
    if tracker_instance:
        tracker_instance.set_build_info(
            commit=os.getenv("AUTOMETRICS_COMMIT") or "",
            version=os.getenv("AUTOMETRICS_VERSION") or "",
        )

    return tracker_instance


def get_tracker_type() -> TrackerType:
    """Get the tracker type."""
    tracker_type = os.getenv("AUTOMETRICS_TRACKER") or "opentelemetry"
    if tracker_type.lower() == "prometheus":
        return TrackerType.PROMETHEUS
    return TrackerType.OPENTELEMETRY


def default_tracker():
    """Setup the default tracker."""
    preferred_tracker = get_tracker_type()
    return init_tracker(preferred_tracker)


tracker: TrackMetrics = default_tracker()


def get_tracker() -> TrackMetrics:
    """Get the tracker type."""
    return tracker


def set_tracker(tracker_type: TrackerType):
    """Set the tracker type."""
    global tracker
    tracker = init_tracker(tracker_type)

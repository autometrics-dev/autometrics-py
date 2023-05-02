from typing import Protocol, Optional
from enum import Enum

from ..objectives import Objective


class Result(Enum):
    """Result of the function call."""

    OK = "ok"
    ERROR = "error"


class TrackMetrics(Protocol):
    """Protocol for tracking metrics."""

    # def start(self, function: str = None, module: str = None):
    #     """Start tracking metrics for a function call."""

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
    # DUMMY = "dummy"


def create_tracker(tracker_type: TrackerType) -> TrackMetrics:
    """Create a tracker"""
    if tracker_type == TrackerType.OPENTELEMETRY:
        print("open yes")
        # pylint: disable=import-outside-toplevel
        from .opentelemetry import OpenTelemetryTracker

        # if isinstance(tracker, OpenTelemetryTracker):
        #     return tracker
        return OpenTelemetryTracker()
    elif tracker_type == TrackerType.PROMETHEUS:
        print("prom yes")
        # pylint: disable=import-outside-toplevel
        from .prometheus import PrometheusTracker

        # if isinstance(tracker, PrometheusTracker):
        #     return tracker
        return PrometheusTracker()
    # elif tracker_type == TrackerType.DUMMY:
    #     return DummyTracker()


# class DummyTracker:
#     def finish(
#         self,
#         start_time: float,
#         function: str,
#         module: str,
#         caller: str,
#         result: Result = Result.OK,
#         objective: Optional[Objective] = None,
#     ):
#         pass

try:
    print("Create open telemetry tracker")
    tracker = create_tracker(TrackerType.OPENTELEMETRY)
except ImportError:
    print("Create prometheus tracker")
    tracker = create_tracker(TrackerType.PROMETHEUS)

# tracker = create_tracker(TrackerType.DUMMY)


def get_tracker() -> TrackMetrics:
    """Get the tracker type."""
    return tracker


def set_tracker(tracker_type: TrackerType):
    """Set the tracker type."""
    # print("Set tracker type", tracker_type.value)
    # pylint: disable=global-statement
    global tracker
    tracker = create_tracker(tracker_type)

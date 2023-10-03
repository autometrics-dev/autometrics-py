from typing import Optional, cast
from opentelemetry.sdk.metrics.export import MetricReader

from .types import TrackerType, TrackMetrics
from .temporary import TemporaryTracker
from ..exposition import create_exporter
from ..settings import AutometricsSettings


_tracker: TrackMetrics = TemporaryTracker()


def get_tracker() -> TrackMetrics:
    """Get the tracker type."""
    global _tracker
    return _tracker


def set_tracker(new_tracker: TrackMetrics):
    """Set the tracker type."""
    global _tracker
    _tracker = new_tracker


def init_tracker(
    tracker_type: TrackerType, settings: AutometricsSettings
) -> TrackMetrics:
    """Create a tracker"""

    tracker_instance: TrackMetrics
    if tracker_type == TrackerType.OPENTELEMETRY:
        # pylint: disable=import-outside-toplevel
        from .opentelemetry import OpenTelemetryTracker

        exporter: Optional[MetricReader] = None
        if settings["exporter"]:
            exporter = create_exporter(settings["exporter"])
        tracker_instance = OpenTelemetryTracker(exporter)
    elif tracker_type == TrackerType.PROMETHEUS:
        # pylint: disable=import-outside-toplevel
        from .prometheus import PrometheusTracker

        if settings["exporter"]:
            exporter = create_exporter(settings["exporter"])
        tracker_instance = PrometheusTracker()
    # NOTE - Only set the build info when the tracker is initialized
    tracker_instance.set_build_info(
        commit=settings["commit"],
        version=settings["version"],
        branch=settings["branch"],
    )

    set_tracker(tracker_instance)
    return tracker_instance

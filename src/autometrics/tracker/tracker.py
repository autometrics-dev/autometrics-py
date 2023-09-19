from typing import Protocol, Optional, cast
from enum import Enum
from opentelemetry.sdk.metrics.export import MetricReader

from .types import TrackerType, TrackMetrics
from .temporary import TemporaryTracker
from ..exposition import PrometheusExporterOptions, get_exporter
from ..settings import get_settings, AutometricsSettings


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
            exporter = get_exporter(settings["exporter"])
        tracker_instance = OpenTelemetryTracker(exporter)
    elif tracker_type == TrackerType.PROMETHEUS:
        # pylint: disable=import-outside-toplevel
        from .prometheus import PrometheusTracker

        if settings["exporter"]:
            from prometheus_client import start_http_server

            if settings["exporter"]["type"] != "prometheus-client":
                raise Exception("Invalid exporter type for Prometheus tracker")
            exporter_settings = cast(PrometheusExporterOptions, settings["exporter"])
            start_http_server(exporter_settings["port"], exporter_settings["address"])
        tracker_instance = PrometheusTracker()
    # NOTE - Only set the build info when the tracker is initialized
    tracker_instance.set_build_info(
        commit=settings["commit"],
        version=settings["version"],
        branch=settings["branch"],
    )

    return tracker_instance


tracker: TrackMetrics = TemporaryTracker()


def get_tracker() -> TrackMetrics:
    """Get the tracker type."""
    return tracker


def set_tracker(tracker_type: TrackerType):
    """Set the tracker type."""
    global tracker
    settings = get_settings()
    settings["tracker"] = tracker_type
    tracker = init_tracker(tracker_type, settings)

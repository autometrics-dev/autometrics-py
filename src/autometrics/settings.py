import os

from opentelemetry.sdk.metrics.export import MetricReader
from typing import List, TypedDict, Optional
from typing_extensions import Unpack

from .tracker.types import TrackerType
from .exposition import ExporterOptions
from .objectives import ObjectiveLatency


class AutometricsSettings(TypedDict):
    """Settings for autometrics."""

    histogram_buckets: List[float]
    tracker: TrackerType
    exporter: Optional[ExporterOptions]
    enable_exemplars: bool
    service_name: str
    commit: str
    version: str
    branch: str


class AutometricsOptions(TypedDict, total=False):
    """User supplied overrides for autometrics settings."""

    histogram_buckets: List[float]
    tracker: str
    exporter: ExporterOptions
    enable_exemplars: bool
    service_name: str
    commit: str
    version: str
    branch: str


def get_objective_boundaries():
    """Get the objective latency boundaries as float values in seconds (instead of strings)"""
    return list(map(lambda c: float(c.value), ObjectiveLatency))


settings: Optional[AutometricsSettings] = None


def init_settings(**overrides: Unpack[AutometricsOptions]) -> AutometricsSettings:
    tracker_setting = (
        overrides.get("tracker") or os.getenv("AUTOMETRICS_TRACKER") or "opentelemetry"
    )
    tracker_type = (
        TrackerType.PROMETHEUS
        if tracker_setting.lower() == "prometheus"
        else TrackerType.OPENTELEMETRY
    )

    config: AutometricsSettings = {
        "histogram_buckets": overrides.get("histogram_buckets")
        or get_objective_boundaries(),
        "enable_exemplars": overrides.get(
            "enable_exemplars", os.getenv("AUTOMETRICS_EXEMPLARS") == "true"
        ),
        "tracker": tracker_type,
        "exporter": overrides.get("exporter"),
        "service_name": overrides.get(
            "service_name",
            os.getenv(
                "AUTOMETRICS_SERVICE_NAME",
                os.getenv("OTEL_SERVICE_NAME", __package__.rsplit(".", 1)[0]),
            ),
        ),
        "commit": overrides.get(
            "commit", os.getenv("AUTOMETRICS_COMMIT", os.getenv("COMMIT_SHA", ""))
        ),
        "branch": overrides.get(
            "branch", os.getenv("AUTOMETRICS_BRANCH", os.getenv("BRANCH_NAME", ""))
        ),
        "version": overrides.get("version", os.getenv("AUTOMETRICS_VERSION", "")),
    }
    validate_settings(config)

    global settings
    settings = config
    return settings


def get_settings() -> AutometricsSettings:
    """Get the current settings."""
    global settings
    if settings is None:
        settings = init_settings()
    return settings


def validate_settings(settings: AutometricsSettings):
    """Ensure that the settings are valid. For example, we don't support Prometheus exporter with OpenTelemetry tracker."""
    if settings["exporter"]:
        if settings["tracker"] == TrackerType.OPENTELEMETRY and not isinstance(
            settings["exporter"], MetricReader
        ):
            if settings["exporter"]["type"] == "prometheus":
                raise ValueError(
                    "Prometheus exporter is not supported with OpenTelemetry tracker"
                )
        if settings["tracker"] == TrackerType.PROMETHEUS:
            if isinstance(settings["exporter"], MetricReader):
                raise ValueError(
                    "OpenTelemetry exporter is not supported with Prometheus tracker"
                )
            if (
                settings["exporter"]["type"] in ["otlp-proto-http", "otlp-proto-grpc"]
            ) or (isinstance(settings["exporter"], MetricReader)):
                raise ValueError(
                    "OTLP exporter is not supported with Prometheus tracker"
                )

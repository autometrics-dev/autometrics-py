import os

from typing import cast, Dict, List, TypedDict, Optional, Union
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
    exporter: Dict[str, Union[str, int, bool]]
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
    exporter: Optional[ExporterOptions] = None
    exporter_option = overrides.get("exporter")
    if exporter_option:
        exporter = cast(ExporterOptions, exporter_option)

    config: AutometricsSettings = {
        "histogram_buckets": overrides.get("histogram_buckets")
        or get_objective_boundaries(),
        "enable_exemplars": overrides.get(
            "enable_exemplars", os.getenv("AUTOMETRICS_EXEMPLARS") == "true"
        ),
        "tracker": tracker_type,
        "exporter": exporter,
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
        exporter_type = settings["exporter"]["type"]
        if settings["tracker"] == TrackerType.OPENTELEMETRY:
            if not exporter_type.startswith("otel") and not exporter_type.startswith(
                "otlp"
            ):
                raise ValueError(
                    f"Exporter type {exporter_type} is not supported with OpenTelemetry tracker."
                )
        if settings["tracker"] == TrackerType.PROMETHEUS:
            if not exporter_type.startswith("prometheus"):
                raise ValueError(
                    f"Exporter type {exporter_type} is not supported with Prometheus tracker."
                )

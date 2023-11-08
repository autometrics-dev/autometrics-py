import os

from typing import cast, Dict, List, TypedDict, Optional, Any
from typing_extensions import Unpack

from .tracker.types import TrackerType
from .exposition import ExporterOptions
from .objectives import ObjectiveLatency
from .utils import extract_repository_provider, read_repository_url_from_fs


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
    repository_url: str
    repository_provider: str


class AutometricsOptions(TypedDict, total=False):
    """User supplied overrides for autometrics settings."""

    histogram_buckets: List[float]
    tracker: str
    exporter: Dict[str, Any]
    enable_exemplars: bool
    service_name: str
    commit: str
    version: str
    branch: str
    repository_url: str
    repository_provider: str


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

    repository_url: Optional[str] = overrides.get(
        "repository_url", os.getenv("AUTOMETRICS_REPOSITORY_URL")
    )
    if repository_url is None:
        repository_url = read_repository_url_from_fs()

    repository_provider: Optional[str] = overrides.get(
        "repository_provider", os.getenv("AUTOMETRICS_REPOSITORY_PROVIDER")
    )
    if repository_provider is None and repository_url is not None:
        repository_provider = extract_repository_provider(repository_url)

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
        "repository_url": repository_url or "",
        "repository_provider": repository_provider or "",
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
    """Ensure that the settings are valid. For example, we don't support OpenTelemetry exporters with Prometheus tracker."""
    if settings["exporter"]:
        exporter_type = settings["exporter"]["type"]
        if settings["tracker"] == TrackerType.PROMETHEUS:
            if exporter_type != "prometheus":
                raise ValueError(
                    f"Exporter type {exporter_type} is not supported with Prometheus tracker."
                )

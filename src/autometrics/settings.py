import os

from typing import List, TypedDict, Optional
from typing_extensions import Unpack

from .objectives import ObjectiveLatency


class AutometricsSettings(TypedDict):
    """Settings for autometrics."""

    histogram_buckets: List[float]
    tracker: str
    enable_exemplars: bool
    service_name: str
    commit: str
    version: str
    branch: str


class AutometricsOptions(TypedDict, total=False):
    """User supplied overrides for autometrics settings."""

    histogram_buckets: List[float]
    tracker: str
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
    config: AutometricsSettings = {
        "histogram_buckets": overrides.get("histogram_buckets")
        or get_objective_boundaries(),
        "tracker": overrides.get("tracker")
        or os.getenv("AUTOMETRICS_TRACKER")
        or "opentelemetry",
        "enable_exemplars": overrides.get(
            "enable_exemplars", os.getenv("AUTOMETRICS_EXEMPLARS") == "true"
        ),
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
    global settings
    settings = config
    return settings


def get_settings() -> AutometricsSettings:
    """Get the current settings."""
    global settings
    if settings is None:
        return init_settings()
    return settings

import pytest

from autometrics import init
from autometrics.exposition import PrometheusExporterOptions
from autometrics.tracker.opentelemetry import OpenTelemetryTracker
from autometrics.tracker.prometheus import PrometheusTracker
from autometrics.tracker.tracker import get_tracker
from autometrics.tracker.types import TrackerType
from autometrics.settings import get_settings


def test_init():
    """Test that the default settings are set correctly"""
    init()
    settings = get_settings()
    assert settings == {
        "histogram_buckets": [
            0.005,
            0.01,
            0.025,
            0.05,
            0.075,
            0.1,
            0.25,
            0.5,
            0.75,
            1.0,
            2.5,
            5.0,
            7.5,
            10.0,
        ],
        "enable_exemplars": False,
        "tracker": TrackerType.OPENTELEMETRY,
        "exporter": None,
        "service_name": "autometrics",
        "commit": "",
        "branch": "",
        "version": "",
        "repository_url": "git@github.com:autometrics-dev/autometrics-py.git",
        "repository_provider": "github",
    }
    tracker = get_tracker()
    assert isinstance(tracker, OpenTelemetryTracker)


def test_init_custom():
    """Test that setting custom settings works correctly"""
    init(
        tracker="prometheus",
        service_name="test",
        enable_exemplars=True,
        version="1.0.0",
        commit="123456",
        branch="main",
    )
    settings = get_settings()
    assert settings == {
        "histogram_buckets": [
            0.005,
            0.01,
            0.025,
            0.05,
            0.075,
            0.1,
            0.25,
            0.5,
            0.75,
            1.0,
            2.5,
            5.0,
            7.5,
            10.0,
        ],
        "enable_exemplars": True,
        "tracker": TrackerType.PROMETHEUS,
        "exporter": None,
        "service_name": "test",
        "commit": "123456",
        "branch": "main",
        "version": "1.0.0",
        "repository_url": "git@github.com:autometrics-dev/autometrics-py.git",
        "repository_provider": "github",
    }
    tracker = get_tracker()
    assert isinstance(tracker, PrometheusTracker)


def test_init_env_vars(monkeypatch):
    """Test that setting custom settings via environment variables works correctly"""
    monkeypatch.setenv("AUTOMETRICS_TRACKER", "prometheus")
    monkeypatch.setenv("AUTOMETRICS_SERVICE_NAME", "test")
    monkeypatch.setenv("AUTOMETRICS_EXEMPLARS", "true")
    monkeypatch.setenv("AUTOMETRICS_VERSION", "1.0.0")
    monkeypatch.setenv("AUTOMETRICS_COMMIT", "123456")
    monkeypatch.setenv("AUTOMETRICS_BRANCH", "main")
    init()
    settings = get_settings()

    assert settings == {
        "histogram_buckets": [
            0.005,
            0.01,
            0.025,
            0.05,
            0.075,
            0.1,
            0.25,
            0.5,
            0.75,
            1.0,
            2.5,
            5.0,
            7.5,
            10.0,
        ],
        "enable_exemplars": True,
        "tracker": TrackerType.PROMETHEUS,
        "exporter": None,
        "service_name": "test",
        "commit": "123456",
        "branch": "main",
        "version": "1.0.0",
        "repository_url": "git@github.com:autometrics-dev/autometrics-py.git",
        "repository_provider": "github",
    }


def test_double_init():
    """Test that calling init twice fails"""
    init()
    with pytest.raises(RuntimeError):
        init()


def test_init_with_exporter():
    """Test that setting exporter works correctly"""
    init(
        tracker="prometheus",
        exporter={
            "type": "prometheus",
        },
    )
    settings = get_settings()
    assert settings == {
        "histogram_buckets": [
            0.005,
            0.01,
            0.025,
            0.05,
            0.075,
            0.1,
            0.25,
            0.5,
            0.75,
            1.0,
            2.5,
            5.0,
            7.5,
            10.0,
        ],
        "enable_exemplars": False,
        "tracker": TrackerType.PROMETHEUS,
        "exporter": PrometheusExporterOptions(type="prometheus"),
        "service_name": "autometrics",
        "commit": "",
        "branch": "",
        "version": "",
        "repository_url": "git@github.com:autometrics-dev/autometrics-py.git",
        "repository_provider": "github",
    }
    tracker = get_tracker()
    assert isinstance(tracker, PrometheusTracker)


def test_init_exporter_validation():
    with pytest.raises(ValueError):
        init(
            tracker="prometheus",
            exporter={
                "type": "otel-custom",
            },
        )


def test_init_repo_meta_suppress_detection():
    init(repository_url="", repository_provider="")
    settings = get_settings()
    assert settings["repository_provider"] is ""
    assert settings["repository_url"] is ""

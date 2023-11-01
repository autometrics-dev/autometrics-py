import pytest


@pytest.fixture()
def reset_environment(monkeypatch):
    import importlib
    import opentelemetry
    import prometheus_client
    from . import initialization
    from .tracker import tracker

    importlib.reload(opentelemetry)
    importlib.reload(prometheus_client)
    importlib.reload(initialization)
    importlib.reload(tracker)
    # we'll set debug to true to ensure calling init more than once will fail whole test
    monkeypatch.setenv("AUTOMETRICS_DEBUG", "true")

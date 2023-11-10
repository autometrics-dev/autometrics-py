import os
import pytest

in_ci = os.getenv("CI", "false") == "true"


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

    # github ci uses https so for tests to pass we force ssh url
    if in_ci:
        monkeypatch.setenv(
            "AUTOMETRICS_REPOSITORY_URL",
            "git@github.com:autometrics-dev/autometrics-py.git",
        )

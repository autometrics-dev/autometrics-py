import pytest

from autometrics.utils import get_repository_url

config1 = """
[core]
    key = value
[remote "origin"]
    key2 = value2
    url = https://github.com/autometrics/autometrics-py.git 
    key3 = value3
[branch "main"]
    some-key = some-value
"""

config2 = """
[core]
    key = value
"""

config3 = """
[core]
    key = value
[remote.origin]
    key2 = value2
    url = ssh://git@github.com:autometrics-dev/autometrics-py.git
    key3 = value3
"""

config4 = """
[remote "upstream"]
    url = "git@autometrics.dev/autometrics-ts.git"

[remote "origin"]
    url = "git@github.com:autometrics-dev/autometrics-py.git"
"""


@pytest.fixture(
    params=[
        (config1, "https://github.com/autometrics/autometrics-py.git"),
        (config2, None),
        (config3, "ssh://git@github.com:autometrics-dev/autometrics-py.git"),
        (config4, "git@github.com:autometrics-dev/autometrics-py.git"),
    ]
)
def git_config(request):
    return request.param


def test_read_repository_url(monkeypatch, git_config):
    """Test that the repository url is read correctly from git config."""
    (config, expected_url) = git_config
    url = get_repository_url(config)
    assert url == expected_url

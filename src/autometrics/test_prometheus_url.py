import pytest

from .prometheus_url import Generator


# Defaults to localhost:9090
@pytest.fixture(name="default_url_generator", autouse=True)
def fixture_default_url() -> Generator:
    """Create a generator that uses the default url."""
    return Generator("myFunction", "myModule")


def test_create_prometheus_url_with_default_url(default_url_generator: Generator):
    """Test that the prometheus url is created correctly."""
    url = default_url_generator.create_prometheus_url("myQuery")

    # Make sure the base URL is correct
    assert url.startswith("http://localhost:9090/graph?g0.expr=")

    # Make sure the query is included in the URL
    assert "myQuery" in url


def test_create_urls_with_default_url(default_url_generator: Generator):
    urls = default_url_generator.create_urls()

    print(urls)

    result = {
        "Request rate URL": "http://localhost:9090/graph?g0.expr=sum%20by%20%28function%2C%20module%2C%20commit%2C%20version%29%20%28rate%20%28function_calls_count_total%7Bfunction%3D%22myFunction%22%2Cmodule%3D%22myModule%22%7D%5B5m%5D%29%20%2A%20on%20%28instance%2C%20job%29%20group_left%28version%2C%20commit%29%20%28last_over_time%28build_info%5B1s%5D%29%20or%20on%20%28instance%2C%20job%29%20up%29%29&g0.tab=0",
        "Latency URL": "http://localhost:9090/graph?g0.expr=sum%20by%20%28le%2C%20function%2C%20module%2C%20commit%2C%20version%29%20%28rate%28function_calls_duration_bucket%7Bfunction%3D%22myFunction%22%2Cmodule%3D%22myModule%22%7D%5B5m%5D%29%20%2A%20on%20%28instance%2C%20job%29%20group_left%28version%2C%20commit%29%20%28last_over_time%28build_info%5B1s%5D%29%20or%20on%20%28instance%2C%20job%29%20up%29%29&g0.tab=0",
        "Error Ratio URL": "http://localhost:9090/graph?g0.expr=sum%20by%20%28function%2C%20module%2C%20commit%2C%20version%29%20%28rate%20%28function_calls_count_total%7Bfunction%3D%22myFunction%22%2Cmodule%3D%22myModule%22%2C%20result%3D%22error%22%7D%5B5m%5D%29%20%2A%20on%20%28instance%2C%20job%29%20group_left%28version%2C%20commit%29%20%28last_over_time%28build_info%5B1s%5D%29%20or%20on%20%28instance%2C%20job%29%20up%29%29%20/%20sum%20by%20%28function%2C%20module%2C%20commit%2C%20version%29%20%28rate%20%28function_calls_count_total%7Bfunction%3D%22myFunction%22%2Cmodule%3D%22myModule%22%7D%5B5m%5D%29%20%2A%20on%20%28instance%2C%20job%29%20group_left%28version%2C%20commit%29%20%28last_over_time%28build_info%5B1s%5D%29%20or%20on%20%28instance%2C%20job%29%20up%29%29&g0.tab=0",
    }
    assert result == urls


@pytest.fixture(name="custom_url_generator", autouse=True)
def fixture_custom_url():
    return Generator("myFunction", "myModule", base_url="http://localhost:9091")


def test_create_prometheus_url_with_custom_url(custom_url_generator: Generator):
    """Test the prometheus url generator with a custom base URL."""
    url = custom_url_generator.create_prometheus_url("myQuery")

    # Make sure the base URL is correct
    assert url.startswith("http://localhost:9091/graph?g0.expr=")

    # Make sure the query is included in the URL
    assert "myQuery" in url

import unittest
from autometrics.prometheus_url import Generator


# Defaults to localhost:9090
class TestPrometheusUrlGeneratorDefault(unittest.TestCase):
    """Test the prometheus url generator with default values."""

    def setUp(self):
        self.generator = Generator("myFunction", "myModule")

    def test_create_prometheus_url(self):
        """Test that the prometheus url is created correctly."""
        url = self.generator.create_prometheus_url("myQuery")
        self.assertTrue(
            url.startswith("http://localhost:9090/graph?g0.expr=")
        )  # Make sure the base URL is correct
        self.assertIn("myQuery", url)  # Make sure the query is included in the URL


# Creates proper urls when given a custom base URL
class TestPrometheusUrlGeneratorCustomUrl(unittest.TestCase):
    """Test the prometheus url generator with a custom base URL."""

    def setUp(self):
        self.generator = Generator(
            "myFunction", "myModule", base_url="http://localhost:9091"
        )

    def test_create_prometheus_url(self):
        """Test that the prometheus url is created correctly."""
        url = self.generator.create_prometheus_url("myQuery")
        self.assertTrue(
            url.startswith("http://localhost:9091/graph?g0.expr=")
        )  # Make sure the base URL is correct
        self.assertIn("myQuery", url)  # Make sure the query is included in the URL

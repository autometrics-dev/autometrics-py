import unittest
from autometrics.prometheus_url import Generator


# Defaults to localhost:9090
class TestPrometheusUrlGeneratorDefault(unittest.TestCase):
    def setUp(self):
        self.generator = Generator("myFunction", "myModule")

    def test_create_prometheus_url(self):
        url = self.generator.create_prometheus_url("myQuery")
        self.assertTrue(
            url.startswith("http://localhost:9090/graph?g0.expr=")
        )  # Make sure the base URL is correct
        self.assertIn("myQuery", url)  # Make sure the query is included in the URL


# Creates proper urls when given a custom base URL
class TestPrometheusUrlGeneratorCustomUrl(unittest.TestCase):
    def setUp(self):
        self.generator = Generator(
            "myFunction", "myModule", base_url="http://localhost:9091"
        )

    def test_create_prometheus_url(self):
        url = self.generator.create_prometheus_url("myQuery")
        self.assertTrue(
            url.startswith("http://localhost:9091/graph?g0.expr=")
        )  # Make sure the base URL is correct
        self.assertIn("myQuery", url)  # Make sure the query is included in the URL


if __name__ == "__main__":
    unittest.main()

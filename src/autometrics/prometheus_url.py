import urllib.parse
import os
from typing import Optional
from dotenv import load_dotenv

ADD_BUILD_INFO_LABELS = "* on (instance, job) group_left(version, commit) (last_over_time(build_info[1s]) or on (instance, job) up)"


def cleanup_url(url: str) -> str:
    """Remove the trailing slash if there is one."""
    if url[-1] == "/":
        url = url[:-1]
    return url


class Generator:
    """Generate prometheus query urls for a given function/module."""

    def __init__(
        self, function_name: str, module_name: str, base_url: Optional[str] = None
    ):
        load_dotenv()
        self.function_name = function_name
        self.module_name = module_name

        url = base_url or os.getenv("PROMETHEUS_URL") or "http://localhost:9090"
        self.base_url = cleanup_url(url)

    def create_urls(self):
        """Create the prometheus query urls for the function and module."""
        request_rate_query = f'sum by (function, module, commit, version) (rate (function_calls_count_total{{function="{self.function_name}",module="{self.module_name}"}}[5m]) {ADD_BUILD_INFO_LABELS})'
        latency_query = f'sum by (le, function, module, commit, version) (rate(function_calls_duration_bucket{{function="{self.function_name}",module="{self.module_name}"}}[5m]) {ADD_BUILD_INFO_LABELS})'
        error_ratio_query = f'sum by (function, module, commit, version) (rate (function_calls_count_total{{function="{self.function_name}",module="{self.module_name}", result="error"}}[5m]) {ADD_BUILD_INFO_LABELS}) / {request_rate_query}'

        queries = {
            "Request rate URL": request_rate_query,
            "Latency URL": latency_query,
            "Error Ratio URL": error_ratio_query,
        }

        urls = {}
        for [name, query] in queries.items():
            # for query in queries:
            generated_url = self.create_prometheus_url(query)
            urls[name] = generated_url
        return urls

    def create_prometheus_url(self, query: str):
        """Create a the full query url for a given query."""
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}/graph?g0.expr={encoded_query}&g0.tab=0"
        return url

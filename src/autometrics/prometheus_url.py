import urllib.parse
import os
from typing import Optional
from dotenv import load_dotenv
from .constants import (ENV_FP_METRICS_URL, ENV_PROMETHEUS_URL_DEPRECATED)

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

        url = base_url or os.getenv(ENV_FP_METRICS_URL) or os.getenv(ENV_PROMETHEUS_URL_DEPRECATED) or "http://localhost:9090"
        self.base_url = cleanup_url(url)

    def create_urls(self):
        """Create the prometheus query urls for the function and module."""
        request_rate_query = f'sum by (function, module) (rate (function_calls_count_total{{function="{self.function_name}",module="{self.module_name}"}}[5m]))'
        latency_query = f'sum by (le, function, module) (rate(function_calls_duration_bucket{{function="{self.function_name}",module="{self.module_name}"}}[5m]))'
        error_ratio_query = f'sum by (function, module) (rate (function_calls_count_total{{function="{self.function_name}",module="{self.module_name}", result="error"}}[5m])) / {request_rate_query}'

        queries = [request_rate_query, latency_query, error_ratio_query]
        names = ["Request rate URL", "Latency URL", "Error Ratio URL"]
        urls = {}
        for name in names:
            for query in queries:
                generated_url = self.create_prometheus_url(query)
                urls[name] = generated_url
                queries.remove(query)
                break
        return urls

    def create_prometheus_url(self, query: str):
        """Create a the full query url for a given query."""
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}/graph?g0.expr={encoded_query}&g0.tab=0"
        return url

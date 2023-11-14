import time
from typing import Optional
from prometheus_client import Counter, Histogram, Gauge

from ..constants import (
    AUTOMETRICS_VERSION_PROMETHEUS,
    COUNTER_NAME_PROMETHEUS,
    HISTOGRAM_NAME_PROMETHEUS,
    CONCURRENCY_NAME_PROMETHEUS,
    REPOSITORY_PROVIDER_PROMETHEUS,
    REPOSITORY_URL_PROMETHEUS,
    SERVICE_NAME_PROMETHEUS,
    BUILD_INFO_NAME,
    COUNTER_DESCRIPTION,
    HISTOGRAM_DESCRIPTION,
    CONCURRENCY_DESCRIPTION,
    BUILD_INFO_DESCRIPTION,
    OBJECTIVE_NAME_PROMETHEUS,
    OBJECTIVE_PERCENTILE_PROMETHEUS,
    OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
    COMMIT_KEY,
    SPEC_VERSION,
    VERSION_KEY,
    BRANCH_KEY,
)

from ..exemplar import get_exemplar
from .types import Result
from ..objectives import Objective
from ..settings import get_settings


class PrometheusTracker:
    """A tracker for Prometheus metrics."""

    prom_counter = Counter(
        COUNTER_NAME_PROMETHEUS,
        COUNTER_DESCRIPTION,
        [
            "function",
            "module",
            SERVICE_NAME_PROMETHEUS,
            "result",
            "caller_module",
            "caller_function",
            OBJECTIVE_NAME_PROMETHEUS,
            OBJECTIVE_PERCENTILE_PROMETHEUS,
        ],
    )
    prom_histogram = Histogram(
        HISTOGRAM_NAME_PROMETHEUS,
        HISTOGRAM_DESCRIPTION,
        [
            "function",
            "module",
            SERVICE_NAME_PROMETHEUS,
            OBJECTIVE_NAME_PROMETHEUS,
            OBJECTIVE_PERCENTILE_PROMETHEUS,
            OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
        ],
        buckets=get_settings()["histogram_buckets"],
        unit="seconds",
    )
    prom_gauge_build_info = Gauge(
        BUILD_INFO_NAME,
        BUILD_INFO_DESCRIPTION,
        [
            COMMIT_KEY,
            VERSION_KEY,
            BRANCH_KEY,
            SERVICE_NAME_PROMETHEUS,
            REPOSITORY_URL_PROMETHEUS,
            REPOSITORY_PROVIDER_PROMETHEUS,
            AUTOMETRICS_VERSION_PROMETHEUS,
        ],
    )
    prom_gauge_concurrency = Gauge(
        CONCURRENCY_NAME_PROMETHEUS,
        CONCURRENCY_DESCRIPTION,
        [
            "function",
            "module",
            SERVICE_NAME_PROMETHEUS,
        ],
    )

    def __init__(self) -> None:
        self._has_set_build_info = False

    def _count(
        self,
        func_name: str,
        module_name: str,
        caller_module: str,
        caller_function: str,
        objective: Optional[Objective] = None,
        exemplar: Optional[dict] = None,
        result: Result = Result.OK,
        inc_by: int = 1,
    ):
        """Increment the counter for the function call."""
        objective_name = "" if objective is None else objective.name
        percentile = (
            ""
            if objective is None or objective.success_rate is None
            else objective.success_rate.value
        )
        service_name = get_settings()["service_name"]

        self.prom_counter.labels(
            func_name,
            module_name,
            service_name,
            result.value,
            caller_module,
            caller_function,
            objective_name,
            percentile,
        ).inc(inc_by, exemplar)

    def _histogram(
        self,
        func_name: str,
        module_name: str,
        duration: float,
        objective: Optional[Objective] = None,
        exemplar: Optional[dict] = None,
    ):
        """Observe the duration of the function call."""

        objective_name = "" if objective is None else objective.name
        latency = None if objective is None else objective.latency
        percentile = ""
        threshold = ""
        if latency is not None:
            threshold = latency[0].value
            percentile = latency[1].value
        service_name = get_settings()["service_name"]

        self.prom_histogram.labels(
            func_name,
            module_name,
            service_name,
            objective_name,
            percentile,
            threshold,
        ).observe(duration, exemplar)

    def set_build_info(self, commit: str, version: str, branch: str):
        if not self._has_set_build_info:
            self._has_set_build_info = True
            service_name = get_settings()["service_name"]
            repository_url = get_settings()["repository_url"]
            repository_provider = get_settings()["repository_provider"]
            self.prom_gauge_build_info.labels(
                commit,
                version,
                branch,
                service_name,
                repository_url,
                repository_provider,
                SPEC_VERSION,
            ).set(1)

    def start(
        self, function: str, module: str, track_concurrency: Optional[bool] = False
    ):
        """Start tracking metrics for a function call."""
        if track_concurrency:
            service_name = get_settings()["service_name"]
            self.prom_gauge_concurrency.labels(function, module, service_name).inc()

    def finish(
        self,
        duration: float,
        function: str,
        module: str,
        caller_module: str,
        caller_function: str,
        result: Result = Result.OK,
        objective: Optional[Objective] = None,
        track_concurrency: Optional[bool] = False,
    ):
        """Finish tracking metrics for a function call."""
        exemplar = None
        if get_settings()["enable_exemplars"]:
            exemplar = get_exemplar()

        self._count(
            function,
            module,
            caller_module,
            caller_function,
            objective,
            exemplar,
            result,
        )
        self._histogram(function, module, duration, objective, exemplar)

        if track_concurrency:
            service_name = get_settings()["service_name"]
            self.prom_gauge_concurrency.labels(function, module, service_name).dec()

    def initialize_counters(
        self,
        function: str,
        module: str,
        objective: Optional[Objective] = None,
    ):
        """Initialize tracking metrics for a function call at zero."""
        caller_module = ""
        caller_function = ""
        self._count(
            function,
            module,
            caller_module,
            caller_function,
            objective,
            None,
            Result.OK,
            0,
        )
        self._count(
            function,
            module,
            caller_module,
            caller_function,
            objective,
            None,
            Result.ERROR,
            0,
        )

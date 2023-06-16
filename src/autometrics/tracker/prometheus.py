import os
import time
from typing import Optional
from prometheus_client import Counter, Histogram, Gauge

from ..constants import (
    COUNTER_NAME_PROMETHEUS,
    HISTOGRAM_NAME_PROMETHEUS,
    CONCURRENCY_NAME_PROMETHEUS,
    BUILD_INFO_NAME,
    COUNTER_DESCRIPTION,
    HISTOGRAM_DESCRIPTION,
    CONCURRENCY_DESCRIPTION,
    BUILD_INFO_DESCRIPTION,
    OBJECTIVE_NAME_PROMETHEUS,
    OBJECTIVE_PERCENTILE_PROMETHEUS,
    OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
    COMMIT_KEY,
    VERSION_KEY,
    BRANCH_KEY,
)

from .exemplar import get_exemplar
from .tracker import Result
from ..objectives import Objective


class PrometheusTracker:
    """A tracker for Prometheus metrics."""

    prom_counter = Counter(
        COUNTER_NAME_PROMETHEUS,
        COUNTER_DESCRIPTION,
        [
            "function",
            "module",
            "result",
            "caller",
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
            OBJECTIVE_NAME_PROMETHEUS,
            OBJECTIVE_PERCENTILE_PROMETHEUS,
            OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
        ],
    )
    prom_gauge_build_info = Gauge(
        BUILD_INFO_NAME, BUILD_INFO_DESCRIPTION, [COMMIT_KEY, VERSION_KEY, BRANCH_KEY]
    )
    prom_gauge_concurrency = Gauge(
        CONCURRENCY_NAME_PROMETHEUS, CONCURRENCY_DESCRIPTION, ["function", "module"]
    )

    def __init__(self) -> None:
        self._has_set_build_info = False

    def _count(
        self,
        func_name: str,
        module_name: str,
        caller: str,
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

        self.prom_counter.labels(
            func_name,
            module_name,
            result.value,
            caller,
            objective_name,
            percentile,
        ).inc(inc_by, exemplar)

    def _histogram(
        self,
        func_name: str,
        module_name: str,
        start_time: float,
        objective: Optional[Objective] = None,
        exemplar: Optional[dict] = None,
    ):
        """Observe the duration of the function call."""
        duration = time.time() - start_time

        objective_name = "" if objective is None else objective.name
        latency = None if objective is None else objective.latency
        percentile = ""
        threshold = ""
        if latency is not None:
            threshold = latency[0].value
            percentile = latency[1].value

        self.prom_histogram.labels(
            func_name,
            module_name,
            objective_name,
            percentile,
            threshold,
        ).observe(duration, exemplar)

    def set_build_info(self, commit: str, version: str, branch: str):
        if not self._has_set_build_info:
            self._has_set_build_info = True
            self.prom_gauge_build_info.labels(commit, version, branch).set(1)

    def start(
        self, function: str, module: str, track_concurrency: Optional[bool] = False
    ):
        """Start tracking metrics for a function call."""
        if track_concurrency:
            self.prom_gauge_concurrency.labels(function, module).inc()

    def finish(
        self,
        start_time: float,
        function: str,
        module: str,
        caller: str,
        result: Result = Result.OK,
        objective: Optional[Objective] = None,
        track_concurrency: Optional[bool] = False,
    ):
        """Finish tracking metrics for a function call."""
        exemplar = None
        if os.getenv("AUTOMETRICS_EXEMPLARS") == "true":
            exemplar = get_exemplar()

        self._count(function, module, caller, objective, exemplar, result)
        self._histogram(function, module, start_time, objective, exemplar)

        if track_concurrency:
            self.prom_gauge_concurrency.labels(function, module).dec()

    def initialize_at_zero(
        self,
        function: str,
        module: str,
        objective: Optional[Objective] = None,
    ):
        """Initialize tracking metrics for a function call at zero."""
        self._count(function, module, None, objective, None, Result.OK, inc_by=0)
        self._count(function, module, None, objective, None, Result.ERROR, inc_by=0)

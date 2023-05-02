import time
from typing import Optional
from prometheus_client import Counter, Histogram
from .emit import Result

from ..constants import (
    COUNTER_NAME_PROMETHEUS,
    HISTOGRAM_NAME_PROMETHEUS,
    COUNTER_DESCRIPTION,
    HISTOGRAM_DESCRIPTION,
    OBJECTIVE_NAME_PROMETHEUS,
    OBJECTIVE_PERCENTILE_PROMETHEUS,
    OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
)
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

    def _count(
        self,
        func_name: str,
        module_name: str,
        caller: str,
        objective: Optional[Objective] = None,
        result: Result = Result.OK,
    ):
        """Increment the counter for the function call."""

        print("prom_counting")

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
        ).inc()

    def _histogram(
        self,
        func_name: str,
        module_name: str,
        start_time: float,
        objective: Optional[Objective] = None,
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
        ).observe(duration)

    # def start(self, function: str = None, module: str = None):
    #     """Start tracking metrics for a function call."""
    #     pass

    def finish(
        self,
        start_time: float,
        function: str,
        module: str,
        caller: str,
        result: Result = Result.OK,
        objective: Optional[Objective] = None,
    ):
        """Finish tracking metrics for a function call."""
        self._count(function, module, caller, objective, result)
        self._histogram(function, module, start_time, objective)

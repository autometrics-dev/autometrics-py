import time
from enum import Enum
from typing import Optional
from prometheus_client import Counter, Histogram

from .constants import (
    COUNTER_DESCRIPTION,
    HISTOGRAM_DESCRIPTION,
    OBJECTIVE_NAME_PROMETHEUS,
    OBJECTIVE_PERCENTILE_PROMETHEUS,
    OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
)
from .objectives import Objective

prom_counter = Counter(
    "function_calls_count",
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
    "function_calls_duration",
    HISTOGRAM_DESCRIPTION,
    [
        "function",
        "module",
        OBJECTIVE_NAME_PROMETHEUS,
        OBJECTIVE_PERCENTILE_PROMETHEUS,
        OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
    ],
)


class Result(Enum):
    """Result of the function call."""

    OK = "ok"
    ERROR = "error"


def count(
    func_name: str,
    module_name: str,
    caller: str,
    objective: Optional[Objective] = None,
    result: Result = Result.OK,
):
    """Increment the counter for the function call."""

    objective_name = "" if objective is None else objective.name
    percentile = (
        ""
        if objective is None or objective.success_rate is None
        else objective.success_rate.value
    )

    prom_counter.labels(
        func_name,
        module_name,
        result,
        caller,
        objective_name,
        percentile,
    ).inc()


def histogram(
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

    prom_histogram.labels(
        func_name,
        module_name,
        objective_name,
        percentile,
        threshold,
    ).observe(duration)

import time
from enum import Enum
from typing import Union
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
    objective: Union[None, Objective] = None,
    result: Result = Result.OK,
):
    """Increment the counter for the function call."""
    prom_counter.labels(
        func_name,
        module_name,
        result,
        caller,
        "" if objective is None else objective.name,
        ""
        if objective is None or objective.success_rate is None
        else objective.success_rate,
    ).inc()


def histogram(
    func_name: str,
    module_name: str,
    start_time: float,
    objective: Union[None, Objective] = None,
):
    """Observe the duration of the function call."""
    duration = time.time() - start_time
    prom_histogram.labels(
        func_name,
        module_name,
        "" if objective is None else objective.name,
        "" if objective is None or objective.latency is None else objective.latency[1],
        "" if objective is None or objective.latency is None else objective.latency[0],
    ).observe(duration)

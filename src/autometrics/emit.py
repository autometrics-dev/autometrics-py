import time
import os
from enum import Enum
from typing import Optional
from prometheus_client import CollectorRegistry, Counter, Histogram, push_to_gateway

from .constants import (
    COUNTER_DESCRIPTION,
    HISTOGRAM_DESCRIPTION,
    OBJECTIVE_NAME_PROMETHEUS,
    OBJECTIVE_PERCENTILE_PROMETHEUS,
    OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
    ENV_FP_METRICS_URL
)
from .objectives import Objective
from .config import get_push_gateway_url, get_app_name, get_is_pushing_metrics

# NOTE - The app name will be the job name in the registry
app_name = get_app_name()

# TODO - Add a debug log that pushing is enabled
is_pushing_metrics = get_is_pushing_metrics()
push_gateway_url = get_push_gateway_url()

# INVESTIGATE - Does adding a registry affect anything in the pull model?
registry = CollectorRegistry()

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
    registry=registry,
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
    registry=registry,
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
        result.value,
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


def push_metrics_if_push_enabled():
    """Push the metrics to the push gateway if there is a push gateway url configured."""
    if is_pushing_metrics:
        push_to_gateway(
            push_gateway_url,
            job=app_name,
            registry=registry,
        )

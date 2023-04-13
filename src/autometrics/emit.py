import time
import os
from enum import Enum
from typing import Optional
from prometheus_client import CollectorRegistry, Counter, Histogram, push_to_gateway
from dotenv import load_dotenv

from .constants import (
    COUNTER_DESCRIPTION,
    HISTOGRAM_DESCRIPTION,
    OBJECTIVE_NAME_PROMETHEUS,
    OBJECTIVE_PERCENTILE_PROMETHEUS,
    OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
)
from .objectives import Objective

load_dotenv()

# TODO - load app name from autometrics.yaml file in project root
#        take inspiration from `find_dotenv` in `dotenv` package
# The app name will be the job name in the registry
app_name = os.getenv("FP_APP_NAME")

# TODO - Add a debug log that pushing is enabled
# TODO - Configure the push gateway url in the autometrics.yaml file?
push_gateway_url = os.getenv("FP_PUSH_GATEWAY_URL")
is_pushing_metrics = push_gateway_url is not None

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
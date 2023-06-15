import os
import time
from typing import Optional

from opentelemetry.metrics import (
    Meter,
    Counter,
    Histogram,
    UpDownCounter,
    set_meter_provider,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation
from opentelemetry.exporter.prometheus import PrometheusMetricReader

from .exemplar import get_exemplar
from .tracker import Result
from ..objectives import Objective, ObjectiveLatency
from ..constants import (
    COUNTER_DESCRIPTION,
    COUNTER_NAME,
    HISTOGRAM_DESCRIPTION,
    HISTOGRAM_NAME,
    BUILD_INFO_NAME,
    BUILD_INFO_DESCRIPTION,
    OBJECTIVE_NAME,
    OBJECTIVE_PERCENTILE,
    OBJECTIVE_LATENCY_THRESHOLD,
)

FUNCTION_CALLS_DURATION_NAME = "function.calls.duration"


def get_objective_boundaries():
    """Get the objective latency boundaries as float values in seconds (instead of strings)"""
    return list(map(lambda c: float(c.value), ObjectiveLatency))


class OpenTelemetryTracker:
    """Tracker for OpenTelemetry."""

    __counter_instance: Counter
    __histogram_instance: Histogram
    __up_down_counter_instance: UpDownCounter

    def __init__(self):
        exporter = PrometheusMetricReader("")
        view = View(
            name=HISTOGRAM_NAME,
            description=HISTOGRAM_DESCRIPTION,
            instrument_name=HISTOGRAM_NAME,
            aggregation=ExplicitBucketHistogramAggregation(
                boundaries=get_objective_boundaries()
            ),
        )
        meter_provider = MeterProvider(metric_readers=[exporter], views=[view])
        set_meter_provider(meter_provider)
        meter = meter_provider.get_meter(name="autometrics")
        self.__counter_instance = meter.create_counter(
            name=COUNTER_NAME, description=COUNTER_DESCRIPTION
        )
        self.__histogram_instance = meter.create_histogram(
            name=HISTOGRAM_NAME,
            description=HISTOGRAM_DESCRIPTION,
        )
        self.__up_down_counter_instance = meter.create_up_down_counter(
            name=BUILD_INFO_NAME,
            description=BUILD_INFO_DESCRIPTION,
        )
        self._has_set_build_info = False

    def __count(
        self,
        function: str,
        module: str,
        caller: str,
        objective: Optional[Objective],
        exemplar: Optional[dict],
        result: Result,
    ):
        objective_name = "" if objective is None else objective.name
        percentile = (
            ""
            if objective is None or objective.success_rate is None
            else objective.success_rate.value
        )
        self.__counter_instance.add(
            1,
            attributes={
                "function": function,
                "module": module,
                "result": result.value,
                "caller": caller,
                OBJECTIVE_NAME: objective_name,
                OBJECTIVE_PERCENTILE: percentile,
            },
        )

    def __histogram(
        self,
        function: str,
        module: str,
        start_time: float,
        objective: Optional[Objective],
        exemplar: Optional[dict],
    ):
        duration = time.time() - start_time

        objective_name = "" if objective is None else objective.name
        latency = None if objective is None else objective.latency
        percentile = ""
        threshold = ""

        if latency is not None:
            threshold = latency[0].value
            percentile = latency[1].value

        self.__histogram_instance.record(
            duration * 1000,
            attributes={
                "function": function,
                "module": module,
                OBJECTIVE_NAME: objective_name,
                OBJECTIVE_PERCENTILE: percentile,
                OBJECTIVE_LATENCY_THRESHOLD: threshold,
            },
        )

    def set_build_info(self, commit: str, version: str, branch: str):
        if not self._has_set_build_info:
            self._has_set_build_info = True
            self.__up_down_counter_instance.add(
                1.0,
                attributes={
                    "commit": commit,
                    "version": version,
                    "branch": branch,
                },
            )

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
        exemplar = None
        # Currently, exemplars are only supported by prometheus-client
        # https://github.com/autometrics-dev/autometrics-py/issues/41
        # if os.getenv("AUTOMETRICS_EXEMPLARS") == "true":
        #     exemplar = get_exemplar()
        self.__count(function, module, caller, objective, exemplar, result)
        self.__histogram(function, module, start_time, objective, exemplar)

import time
from typing import Dict, Optional, Mapping

from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import (
    Counter,
    Histogram,
    UpDownCounter,
    set_meter_provider,
)
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation
from opentelemetry.sdk.metrics.export import MetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.util.types import AttributeValue

from ..exemplar import get_exemplar
from .types import Result
from ..objectives import Objective, ObjectiveLatency
from ..constants import (
    AUTOMETRICS_VERSION,
    CONCURRENCY_NAME,
    CONCURRENCY_DESCRIPTION,
    COUNTER_DESCRIPTION,
    COUNTER_NAME,
    HISTOGRAM_DESCRIPTION,
    HISTOGRAM_NAME,
    BUILD_INFO_NAME,
    BUILD_INFO_DESCRIPTION,
    REPOSITORY_PROVIDER,
    REPOSITORY_URL,
    SERVICE_NAME,
    OBJECTIVE_NAME,
    OBJECTIVE_PERCENTILE,
    OBJECTIVE_LATENCY_THRESHOLD,
    SPEC_VERSION,
)
from ..settings import get_settings

LabelValue = AttributeValue
Attributes = Dict[str, LabelValue]


def get_resource_attrs() -> Attributes:
    attrs: Attributes = {}
    if get_settings()["service_name"] is not None:
        attrs[ResourceAttributes.SERVICE_NAME] = get_settings()["service_name"]
    if get_settings()["version"] is not None:
        attrs[ResourceAttributes.SERVICE_VERSION] = get_settings()["version"]
    return attrs


class OpenTelemetryTracker:
    """Tracker for OpenTelemetry."""

    __counter_instance: Counter
    __histogram_instance: Histogram
    __up_down_counter_build_info_instance: UpDownCounter
    __up_down_counter_concurrency_instance: UpDownCounter

    def __init__(self, reader: Optional[MetricReader] = None):
        view = View(
            name=HISTOGRAM_NAME,
            description=HISTOGRAM_DESCRIPTION,
            instrument_name=HISTOGRAM_NAME,
            aggregation=ExplicitBucketHistogramAggregation(
                boundaries=get_settings()["histogram_buckets"]
            ),
        )
        resource = Resource.create(get_resource_attrs())
        readers = [reader or PrometheusMetricReader()]
        meter_provider = MeterProvider(
            views=[view],
            resource=resource,
            metric_readers=readers,
        )
        set_meter_provider(meter_provider)
        meter = meter_provider.get_meter(name="autometrics")
        self.__counter_instance = meter.create_counter(
            name=COUNTER_NAME, description=COUNTER_DESCRIPTION
        )
        self.__histogram_instance = meter.create_histogram(
            name=HISTOGRAM_NAME,
            description=HISTOGRAM_DESCRIPTION,
            unit="seconds",
        )
        self.__up_down_counter_build_info_instance = meter.create_up_down_counter(
            name=BUILD_INFO_NAME,
            description=BUILD_INFO_DESCRIPTION,
        )
        self.__up_down_counter_concurrency_instance = meter.create_up_down_counter(
            name=CONCURRENCY_NAME,
            description=CONCURRENCY_DESCRIPTION,
        )
        self._has_set_build_info = False

    def __count(
        self,
        function: str,
        module: str,
        caller_module: str,
        caller_function: str,
        objective: Optional[Objective],
        exemplar: Optional[dict],
        result: Result,
        inc_by: int = 1,
    ):
        objective_name = "" if objective is None else objective.name
        percentile = (
            ""
            if objective is None or objective.success_rate is None
            else objective.success_rate.value
        )
        self.__counter_instance.add(
            inc_by,
            attributes={
                "function": function,
                "module": module,
                "result": result.value,
                "caller.module": caller_module,
                "caller.function": caller_function,
                OBJECTIVE_NAME: objective_name,
                OBJECTIVE_PERCENTILE: percentile,
                SERVICE_NAME: get_settings()["service_name"],
            },
        )

    def __histogram(
        self,
        function: str,
        module: str,
        duration: float,
        objective: Optional[Objective],
        exemplar: Optional[dict],
    ):
        objective_name = "" if objective is None else objective.name
        latency = None if objective is None else objective.latency
        percentile = ""
        threshold = ""

        if latency is not None:
            threshold = latency[0].value
            percentile = latency[1].value

        self.__histogram_instance.record(
            duration,
            attributes={
                "function": function,
                "module": module,
                SERVICE_NAME: get_settings()["service_name"],
                OBJECTIVE_NAME: objective_name,
                OBJECTIVE_PERCENTILE: percentile,
                OBJECTIVE_LATENCY_THRESHOLD: threshold,
            },
        )

    def set_build_info(self, commit: str, version: str, branch: str):
        if not self._has_set_build_info:
            self._has_set_build_info = True
            self.__up_down_counter_build_info_instance.add(
                1.0,
                attributes={
                    "commit": commit,
                    "version": version,
                    "branch": branch,
                    SERVICE_NAME: get_settings()["service_name"],
                    REPOSITORY_URL: get_settings()["repository_url"],
                    REPOSITORY_PROVIDER: get_settings()["repository_provider"],
                    AUTOMETRICS_VERSION: SPEC_VERSION,
                },
            )

    def start(
        self,
        function: str,
        module: str,
        track_concurrency: Optional[bool] = False,
    ):
        """Start tracking metrics for a function call."""
        if track_concurrency:
            self.__up_down_counter_concurrency_instance.add(
                1.0,
                attributes={
                    "function": function,
                    "module": module,
                    SERVICE_NAME: get_settings()["service_name"],
                },
            )

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
        # Currently, exemplars are only supported by prometheus-client
        # https://github.com/autometrics-dev/autometrics-py/issues/41
        # if get_settings()["exemplars"]:
        #     exemplar = get_exemplar()
        self.__count(
            function,
            module,
            caller_module,
            caller_function,
            objective,
            exemplar,
            result,
        )
        self.__histogram(function, module, duration, objective, exemplar)
        if track_concurrency:
            self.__up_down_counter_concurrency_instance.add(
                -1.0,
                attributes={
                    "function": function,
                    "module": module,
                    SERVICE_NAME: get_settings()["service_name"],
                },
            )

    def initialize_counters(
        self,
        function: str,
        module: str,
        objective: Optional[Objective] = None,
    ):
        """Initialize tracking metrics for a function call at zero."""
        caller_module = ""
        caller_function = ""
        self.__count(
            function,
            module,
            caller_module,
            caller_function,
            objective,
            None,
            Result.OK,
            0,
        )
        self.__count(
            function,
            module,
            caller_module,
            caller_function,
            objective,
            None,
            Result.ERROR,
            0,
        )

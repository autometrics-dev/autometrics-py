from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    MetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server
from pydantic import ConfigDict, TypeAdapter
from typing import Dict, Literal, Optional, Union
from typing_extensions import TypedDict

# GRPC is optional so we'll only type it if it's available
try:
    from grpc import ChannelCredentials  # type: ignore
except ImportError:
    ChannelCredentials = None


# All of these are split into two parts because having
# a wall of Optional[...] is not very readable and Required[...] is 3.11+
class OtlpGrpcExporterBase(TypedDict):
    """Base type for OTLP GRPC exporter configuration."""

    type: Literal["otlp-proto-grpc"]


class OtlpGrpcExporterOptions(OtlpGrpcExporterBase, total=False):
    """Configuration for OTLP GRPC exporter."""

    __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)  # type: ignore
    endpoint: str
    insecure: bool
    headers: Dict[str, str]
    credentials: ChannelCredentials
    push_interval: int
    timeout: int
    preferred_temporality: Dict[type, AggregationTemporality]


OtlpGrpcExporterValidator = TypeAdapter(OtlpGrpcExporterOptions)


class OtlpHttpExporterBase(TypedDict):
    """Base type for OTLP HTTP exporter configuration."""

    type: Literal["otlp-proto-http"]


class OtlpHttpExporterOptions(OtlpHttpExporterBase, total=False):
    """Configuration for OTLP HTTP exporter."""

    endpoint: str
    headers: Dict[str, str]
    push_interval: int
    timeout: int
    preferred_temporality: Dict[type, AggregationTemporality]


OtlpHttpExporterValidator = TypeAdapter(OtlpHttpExporterOptions)


class PrometheusExporterBase(TypedDict):
    """Base type for OTLP Prometheus exporter configuration."""

    type: Literal["prometheus"]


class PrometheusExporterOptions(PrometheusExporterBase, total=False):
    """Configuration for Prometheus exporter."""

    address: str
    port: int


PrometheusValidator = TypeAdapter(PrometheusExporterOptions)


class OtelCustomExporterBase(TypedDict):
    """Base type for OTLP Prometheus exporter configuration."""

    type: Literal["otel-custom"]


class OtelCustomExporterOptions(OtelCustomExporterBase, total=False):
    """Configuration for OpenTelemetry Prometheus exporter."""

    __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)  # type: ignore
    exporter: MetricReader


OtelCustomValidator = TypeAdapter(OtelCustomExporterOptions)


ExporterOptions = Union[
    OtlpGrpcExporterOptions,
    OtlpHttpExporterOptions,
    PrometheusExporterOptions,
    OtelCustomExporterOptions,
]


def create_exporter(config: ExporterOptions) -> Optional[MetricReader]:
    """Create an exporter based on the configuration."""
    if config["type"] == "prometheus":
        config = PrometheusValidator.validate_python(config)
        start_http_server(
            config.get("port", 9464),
            config.get("address", "0.0.0.0"),
        )
        return PrometheusMetricReader()
    if config["type"] == "otlp-proto-http":
        config = OtlpHttpExporterValidator.validate_python(config)
        try:
            from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
                OTLPMetricExporter as OTLPHTTPMetricExporter,
            )

            http_exporter = OTLPHTTPMetricExporter(
                endpoint=config.get("endpoint", None),
                headers=config.get("headers", None),
                timeout=config.get("timeout", None),
                preferred_temporality=config.get("preferred_temporality", {}),
            )
            http_reader = PeriodicExportingMetricReader(
                http_exporter,
                export_interval_millis=config.get("push_interval", None),
                export_timeout_millis=config.get("timeout", None),
            )
            return http_reader
        except ImportError:
            raise ImportError("OTLP exporter (HTTP) not installed")
    if config["type"] == "otlp-proto-grpc":
        config = OtlpGrpcExporterValidator.validate_python(config)
        try:
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (  # type: ignore
                OTLPMetricExporter as OTLPGRPCMetricExporter,
            )

            grpc_exporter = OTLPGRPCMetricExporter(
                endpoint=config.get("endpoint", None),
                insecure=config.get("insecure", None),
                credentials=config.get("credentials", None),
                headers=config.get("headers", None),
                timeout=config.get("timeout", None),
                preferred_temporality=config.get("preferred_temporality", {}),
            )
            grpc_reader = PeriodicExportingMetricReader(
                grpc_exporter,
                export_interval_millis=config.get("push_interval", None),
                export_timeout_millis=config.get("timeout", None),
            )
            return grpc_reader
        except ImportError:
            raise ImportError("OTLP exporter (GRPC) not installed")
    if config["type"] == "otel-custom":
        config = OtelCustomValidator.validate_python(config)
        return config.get("exporter", None)
    else:
        raise ValueError("Invalid exporter type")

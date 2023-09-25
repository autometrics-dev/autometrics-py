from typing import cast, Dict, Literal, TypedDict, Optional, Union
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    MetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.exporter.prometheus import PrometheusMetricReader

# GRPC is optional so we'll only type it if it's available
try:
    from grpc import ChannelCredentials  # type: ignore
except ImportError:
    ChannelCredentials = None


class OTLPExporterOptions(TypedDict):
    """Configuration for OTLP exporters."""

    type: Literal["otlp-proto-http", "otlp-proto-grpc"]
    endpoint: str
    insecure: bool
    headers: Dict[str, str]
    credentials: ChannelCredentials
    push_interval: int
    timeout: int
    preferred_temporality: Dict[type, AggregationTemporality]


class OTELPrometheusExporterOptions(TypedDict):
    type: Literal["otel-prometheus"]
    prefix: str


class PrometheusExporterOptions(TypedDict):
    """Configuration for Prometheus exporter."""

    type: Literal["prometheus-client"]
    address: str
    port: int
    prefix: str


ExporterOptions = Union[
    OTLPExporterOptions,
    OTELPrometheusExporterOptions,
    PrometheusExporterOptions,
    MetricReader,
]


def get_exporter(config: ExporterOptions) -> MetricReader:
    if isinstance(config, MetricReader):
        return config
    if config["type"] == "otel-prometheus":
        config = cast(OTELPrometheusExporterOptions, config)
        return PrometheusMetricReader(config.get("prefix", ""))
    if config["type"] == "otlp-proto-http":
        config = cast(OTLPExporterOptions, config)
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
        config = cast(OTLPExporterOptions, config)
        try:
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
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
    else:
        raise ValueError("Invalid exporter type")

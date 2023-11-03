import time
from autometrics import autometrics, init

# Autometrics supports exporting metrics to OTLP collectors via gRPC and HTTP transports.
# This example uses the gRPC transport, available settings are similar to the OpenTelemetry
# Python SDK. By default, the OTLP exporter will send metrics to localhost:4317.
# If you don't have an OTLP collector running, you can run Tilt or Docker Compose
# to start one up.

init(
    exporter={
        "type": "otlp-proto-grpc",
        "push_interval": 1000,
    },
    service_name="otlp-exporter",
)


@autometrics
def my_function():
    pass


while True:
    my_function()
    time.sleep(1)

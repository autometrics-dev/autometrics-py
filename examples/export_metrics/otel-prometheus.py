import time
from autometrics import autometrics, init

# Autometrics supports exporting metrics to Prometheus via the OpenTelemetry.
# This example uses the Prometheus Python client, available settings are same as the
# Prometheus Python client. By default, the Prometheus exporter will expose metrics
# on port 9464. If you don't have a Prometheus server running, you can run Tilt or
# Docker Compose from the root of this repo to start one up.

init(
    tracker="opentelemetry",
    exporter={
        "type": "prometheus",
        "port": 9464,
    },
    service_name="my-service",
)


@autometrics
def my_function():
    pass


while True:
    my_function()
    time.sleep(1)

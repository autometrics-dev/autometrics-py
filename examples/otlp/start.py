import time
from autometrics import autometrics, init

init(
    exporter={"type": "otlp-proto-grpc", "endpoint": "http://localhost:4317"},
    service_name="my-service",
)


@autometrics
def my_function():
    pass


while True:
    my_function()
    time.sleep(1)

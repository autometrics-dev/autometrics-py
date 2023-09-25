import time
from autometrics import autometrics, init

init(
    exporter={
        "type": "otlp-proto-http",
    },
    service_name="my-service",
)


@autometrics
def my_function():
    pass


while True:
    my_function()
    time.sleep(1)

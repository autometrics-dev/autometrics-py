from time import sleep
from autometrics import autometrics, init

from prometheus_client import generate_latest


@autometrics
def foo():
    return "foo"


foo()

init(
    version="1.0.0",
    commit="123456789",
    branch="main",
    exporter={
        "type": "otlp-proto-grpc",
        "endpoint": "localhost:4317",
        "insecure": True,
    },
)

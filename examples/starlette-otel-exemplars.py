import uvicorn

from autometrics import autometrics, init
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import generate_latest
from starlette import applications
from starlette.responses import PlainTextResponse
from starlette.routing import Route

# Let's start by setting up the OpenTelemetry SDK with some defaults
provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Now we can instrument our Starlette application
tracer = trace.get_tracer(__name__)

# Exemplars support requires some additional configuration on autometrics,
# so we need to initialize it with the proper settings
init(tracker="prometheus", enable_exemplars=True, service_name="starlette")


# We need to add tracer decorator before autometrics so that we see the spans
@tracer.start_as_current_span("request")
@autometrics
def outer_function(request):
    response = inner_function()
    return PlainTextResponse(response)


# This function will also get an exemplar because it is called within
# the span of the outer_function
@autometrics
def inner_function():
    return "Hello world!"


def metrics(request):
    # Exemplars are not supported by default prometheus format, so we specifically
    # make an endpoint that uses the OpenMetrics format that supports exemplars.
    body = generate_latest(REGISTRY)
    return PlainTextResponse(body, media_type="application/openmetrics-text")


app = applications.Starlette(
    routes=[Route("/", outer_function), Route("/metrics", metrics)]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

# Start the app and make some requests to http://127.0.0.1:8080/, you should see the spans in the console.
# With autometrics extension installed, you can now hover over the hello handler
# and see the charts and queries associated with them. Open one of the queries
# in Prometheus and you should see exemplars added to the metrics. Don't forget
# to click the Show Exemplars button in Prometheus to see them!

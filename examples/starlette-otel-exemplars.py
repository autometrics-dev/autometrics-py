from opentelemetry import trace
from autometrics import autometrics
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import generate_latest
from starlette import applications
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

# Let's start by setting up the OpenTelemetry SDK with some defaults
provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Now we can instrument our Starlette application
tracer = trace.get_tracer(__name__)


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
    # make an endpoint that uses the OpenMetrics format that supoorts exemplars.
    body = generate_latest(REGISTRY)
    return PlainTextResponse(body, media_type="application/openmetrics-text")


app = applications.Starlette(
    routes=[Route("/", outer_function), Route("/metrics", metrics)]
)

# Now, start the app (env variables are required to enable exemplars):
# AUTOMETRICS_TRACKER=prometheus AUTOMETRICS_EXEMPLARS=true uvicorn starlette-otel-exemplars:app --port 8080
# And make some requests to /. You should see the spans in the console.
# With autometrics extension installed, you can now hover over the hello handler
# and see the charts and queries associated with them. Open one of the queries
# in Prometheus and you should see exemplars added to the metrics. Don't forget
# to click the Show Exemplars button in Prometheus to see them!

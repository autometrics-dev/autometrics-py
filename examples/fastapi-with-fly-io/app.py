import time
from autometrics import autometrics
from autometrics.objectives import Objective, ObjectiveLatency, ObjectivePercentile
from fastapi import FastAPI, Response
from prometheus_client import start_http_server
import uvicorn

app = FastAPI()


# Set up the root endpoint of the API
@app.get("/")
# Add the autometrics decorator to enable metrics for this endpoint
# It needs to be added AFTER the fastapi decorator otherwise it won't
# be triggered
@autometrics
def hello_world():
    do_something()
    return {"Hello": "World"}


# Let's set up an SLO, so we can check out
ITEM_SLO = Objective(
    "sleep",
    success_rate=ObjectivePercentile.P99_9,
    latency=(ObjectiveLatency.Ms250, ObjectivePercentile.P99),
)


@app.get("/sleep/")
@autometrics(objective=ITEM_SLO)
def get_sleep(duration: int = 0):
    """A function that takes a duration parameter to determine how much the response
    needs to be delayed"""

    time.sleep(duration)
    return {"duration": duration}


@app.get("/not-implemented")
@autometrics
def not_implemented():
    """An endpoint that always throws an exception"""
    raise NotImplementedError("Not implemented")


@autometrics
def do_something():
    # This function doesn't do much
    print("done")


# In order for prometheus to get the data we'll set
# up a separate endpoint that exposes data in a format
# that prometheus can understand.
# This metrics server will run on port 8008
start_http_server(8008)

# If the app is not run by fly.io in a container but using python
# directly we enter this flow and it is run on port 8080
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)

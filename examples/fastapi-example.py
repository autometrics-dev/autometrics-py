import asyncio
from fastapi import FastAPI, Response
import uvicorn
from autometrics import autometrics
from prometheus_client import generate_latest

app = FastAPI()


# Set up a metrics endpoint for Prometheus to scrape
# `generate_latest` returns the latest metrics data in the Prometheus text format
@app.get("/metrics")
def metrics():
    return Response(generate_latest())


# Set up the root endpoint of the API
@app.get("/")
@autometrics
def read_root():
    do_something()
    return {"Hello": "World"}


# Set up an async handler
@app.get("/async")
@autometrics
async def async_route():
    message = await do_something_async()
    return {"Hello": message}


@autometrics
def do_something():
    print("done")


@autometrics
async def do_something_async():
    print("async start")
    await asyncio.sleep(2.0)
    print("async done")
    return "async world"


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)

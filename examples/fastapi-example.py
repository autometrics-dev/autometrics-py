import asyncio
import uvicorn

from autometrics import autometrics, init
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
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


def response_is_error(response: Response):
    if response.status_code >= 400:
        return True


@app.get("/not-implemented")
@autometrics(record_error_if=response_is_error)
def not_implemented():
    return JSONResponse(
        status_code=501, content={"message": "This endpoint is not implemented"}
    )


@app.get("/flowers/{flower_name}")
def flower(flower_name: str):
    try:
        return JSONResponse(content={"message": get_pretty_flower(flower_name)})
    except NotFoundError as error:
        return JSONResponse(status_code=404, content={"message": str(error)})


class NotFoundError(Exception):
    pass


def is_not_found_error(error: Exception):
    return isinstance(error, NotFoundError)


@autometrics(record_success_if=is_not_found_error)
def get_pretty_flower(flower_name: str):
    """Returns whether the flower is pretty"""
    print(f"Getting pretty flower for {flower_name}")
    flowers = ["rose", "tulip", "daisy"]
    if flower_name not in flowers:
        raise NotFoundError(
            f"Flower {flower_name} not found. Perhaps you meant one of these: {', '.join(flowers)}?"
        )
    return f"A {flower_name} is pretty"


init(service_name="fastapi-example")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

from fastapi import FastAPI, Response
import uvicorn
from autometrics.autometrics import autometrics
from prometheus_client import generate_latest

app = FastAPI()


@app.get("/metrics")
def metrics():
    return Response(generate_latest())


@app.get("/")
@autometrics
def read_root():
    do_something()
    return {"Hello": "World"}


@autometrics
def do_something():
    print("done")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)

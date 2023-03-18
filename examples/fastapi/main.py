from typing import Union

from fastapi import FastAPI

from autometrics.autometrics import autometrics
from prometheus_client import generate_latest, CollectorRegistry
metrics_reg = CollectorRegistry()

app = FastAPI()


@app.get('/metrics')
def get_metrics():
    return generate_latest(metrics_reg)

@app.get("/")
@autometrics
def read_root():
    return {"Hello": "World"}

@autometrics
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


def generate_random_trafic():
    print("Something")

help(read_item)

from typing import Union

from fastapi import FastAPI
from autometrics.autometrics import autometrics


app = FastAPI()

@autometrics
@app.get("/")
def read_root():
    return {"Hello": "World"}

@autometrics
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


def generate_random_trafic():
    print("Something")

help(read_root)
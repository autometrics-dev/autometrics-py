from fastapi import FastAPI, Response
import uvicorn
from autometrics.autometrics import autometrics
from prometheus_client import generate_latest

app = FastAPI()

@app.get("/metrics")
async def metrics():
    return Response(generate_latest())

@autometrics
@app.get("/")
async def read_root():
    print("This is inside the read_root")
    do_something()
    return {"Hello": "World"}

@autometrics
def do_something():
    print("done")

print(read_root.__doc__)
print(do_something.__doc__)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
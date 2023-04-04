print("hello")
from prometheus_client import start_http_server


@autometrics
def message():
    return "hello"


@autometrics
def greet(name):
    m = message()
    greeting = f"hello {name}, {m}"
    return greeting


start_http_server(8080)
while True:
    greet("john")

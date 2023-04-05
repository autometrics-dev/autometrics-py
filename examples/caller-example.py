from prometheus_client import start_http_server
from autometrics.autometrics import autometrics
import time
import random


# This is moana, who would rather explore the ocean than prometheus metrics
@autometrics
def moana():
    return "surf's up!"


# This is neo, the one (that we'll end up calling)
@autometrics
def neo():
    return "i know kung fu"


# This is simba. Rawr.
@autometrics
def simba():
    return "rawr"


# Define a function that randomly calls `moana`, `neo`, or `simba`
@autometrics
def destiny():
    random_int = random.randint(0, 2)
    if random_int == 0:
        return f"Destiny is calling moana. moana says: {moana()}"
    elif random_int == 1:
        return f"Destiny is calling neo. neo says: {neo()}"
    else:
        return f"Destiny is calling simba. simba says: {simba()}"


# Start an HTTP server on port 8080 using the Prometheus client library, which exposes our metrics to prometheus
start_http_server(8080)

print(f"Try this PromQL query in your Prometheus dashboard:\n")
print(
    f"# Rate of calls to the `destiny` function per second, averaged over 5 minute windows\n"
)
print(
    'sum by (function, module) (rate(function_calls_count_total{caller="destiny"}[5m]))'
)

# Enter an infinite loop (with a 1 second sleep period), calling the `destiny` and `agent_smith` methods.
while True:
    destiny()
    time.sleep(0.3)


# NOTE - You will want to open prometheus

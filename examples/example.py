import time
import random
from autometrics import autometrics, init
from autometrics.objectives import Objective, ObjectiveLatency, ObjectivePercentile


# Defines a class called `Operations`` that has two methods:
#   1. `add` - Perform addition
#   2. `div_handled` - Perform division and handle errors
#
class Operations:
    def __init__(self, **args):
        self.args = args

    @autometrics
    def add(self, num1, num2):
        self.num1 = num1
        self.num2 = num2
        return self.num1 + self.num2

    @autometrics
    def div_handled(self, num1, num2):
        self.num1 = num1
        self.num2 = num2
        try:
            result = self.num1 / self.num2
        except Exception as e:
            result = e.__class__.__name__
        return result


# Perform division without handling errors
@autometrics
def div_unhandled(num1, num2):
    result = num1 / num2
    return result


RANDOM_SLO = Objective(
    "random",
    success_rate=ObjectivePercentile.P99_9,
    latency=(ObjectiveLatency.Ms250, ObjectivePercentile.P99),
)


@autometrics(objective=RANDOM_SLO)
def random_error():
    """This function will randomly return an error or ok."""

    result = random.choice(["ok", "error"])
    if result == "error":
        time.sleep(1)
        raise RuntimeError("random error")
    return result


ops = Operations()

# Show the docstring (with links to prometheus metrics) for the `add` method
print(ops.add.__doc__)

# Show the docstring (with links to prometheus metrics) for the `div_unhandled` method
print(div_unhandled.__doc__)

# Initialize autometrics and start an HTTP server on port 8080 using
# the Prometheus client library, which exposes our metrics to prometheus
init(exporter={"type": "prometheus", "port": 8080})

# Enter an infinite loop (with a 2 second sleep period), calling the "div_handled", "add", and "div_unhandled" methods,
# in order to generate metrics.
while True:
    try:
        ops.div_handled(2, 0)
    except Exception:
        pass

    ops.add(1, 2)
    ops.div_handled(2, 1)

    try:
        # Randomly call `div_unhandled` with a 50/50 chance of raising an error
        div_unhandled(2, random.randint(0, 1))
    except Exception:
        pass

    ops.add(1, 2)
    time.sleep(2)

    try:
        # Call `div_unhandled` such that it raises an error
        div_unhandled(2, 0)
    except Exception:
        pass

    try:
        # Call random_error. It will randomly raise an error or return "ok"
        random_error()
    except Exception:
        pass

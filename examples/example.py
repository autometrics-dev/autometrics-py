from prometheus_client import start_http_server
from autometrics.autometrics import autometrics
import time


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


@autometrics
def div_unhandled(num1, num2):
    result = num1 / num2
    return result


@autometrics
def text_print():
    return "hello"


ops = Operations()

print(ops.add.__doc__)
print(div_unhandled.__doc__)

start_http_server(8080)
while True:
    ops.div_handled(2, 0)
    ops.add(1, 2)
    ops.div_handled(2, 1)
    div_unhandled(2, 0)
    text_print()
    ops.add(1, 2)
    time.sleep(2)
    div_unhandled(2, 0)

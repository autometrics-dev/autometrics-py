from prometheus_client import start_http_server
from autometrics import autometrics
import time

@autometrics
class Operations:
    def __init__(self, **args):
        self.args = args

    def add(self, num1, num2):
        self.num1 = num1
        self.num2 = num2
        return self.num1 + self.num2

    def div_handled(self, num1, num2):
        self.num1 = num1
        self.num2 = num2
        try:
            result = self.num1/self.num2
        except Exception as e:
            result = e.__class__.__name__
        return result

@autometrics
def div_unhandled(num1,num2):
    result = num1 / num2
    return result   

ops = Operations()
start_http_server(8080)
while True:
    print(ops.div_handled(2, 0))
    time.sleep(1)
    print(ops.add(1, 2))
    time.sleep(2)
    print(div_unhandled(2, 0))
    print("server can still run")
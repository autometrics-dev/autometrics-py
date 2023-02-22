from prometheus_client import start_http_server
import time
import autometrics

@autometrics.autometrics
class Operations:
    def __init__(self, **args):
        self.args = args

    def add(self, num1, num2):
        self.num1 = num1
        self.num2 = num2
        return self.num1 + self.num2

    def div(self, num1, num2):
        self.num1 = num1
        self.num2 = num2
        try:
            result = self.num1/self.num2
            return result
        except:
            return "num2 cannot be 0"

# def example():
#     start_time = time.time()
#     print('This is an example function')
#     end_time = time.time()
#     duration = end_time - start_time
#     print('Duration:', duration)

# start_http_server(8080)
# while True:
#     example()
#     time.sleep(1)

ops = Operations()
start_http_server(8080)
while True:
    print(ops.add(1,2))
    time.sleep(1)
    print(ops.div(20,0))
    time.sleep(1)

from prometheus_client import start_http_server
import time
import autometrics

@autometrics.function_calls_count
@autometrics.function_calls_duration
@autometrics.function_calls_concurrent

def example():
    '''prints Hello World'''
    print("Hello World")


print(example.__name__)
from prometheus_client import start_http_server
import time
import autometrics

@autometrics.function_calls_count
@autometrics.function_calls_duration
@autometrics.function_calls_concurrent

def example():
    start_time = time.time()
    print('This is an example function')
    end_time = time.time()
    duration = end_time - start_time
    print('Duration:', duration)

start_http_server(8080)

while True:
    example()
    time.sleep(1)
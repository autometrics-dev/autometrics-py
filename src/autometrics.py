from prometheus_client import Counter, Histogram, Gauge
import time
import inspect
import os

prom_counter = Counter('function_calls_count', 'query??', ['function', 'module', 'result'])
prom_histogram = Histogram('function_calls_duration', 'query??', ['function', 'module'])
# prom_guage = Gauge('function_calls_concurrent', 'query??', ['function', 'module']) # we are not doing gauge atm

def autometrics(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name_path = inspect.getsourcefile(func)
        module_name = os.path.relpath(func_name, start=module_name_path)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            prom_counter.labels(func_name, module_name, 'ok').inc()
        except Exception as e:
            result = "Exception caught"
            prom_counter.labels(func_name, module_name, 'error').inc()
        duration = time.time() - start_time
        prom_histogram.labels(func_name, module_name).observe(duration)
        return result
    return wrapper
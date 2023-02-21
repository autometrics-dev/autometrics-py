from prometheus_client import Counter, Histogram, Gauge
import time
import inspect

prom_counter = Counter('function_calls_count', 'query??', ['function', 'module'])
prom_histogram = Histogram('function_calls_duration', 'query??', ['function', 'module'])
prom_guage = Gauge('function_calls_concurrent', 'query??', ['function', 'module'])

def autometrics(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = inspect.getmodule(func).__name__
        prom_counter.labels(func_name, module_name).inc()
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        prom_histogram.labels(func_name, module_name).observe(duration)
        prom_guage.labels(func_name, module_name).set(time.time())
        return result
    return wrapper

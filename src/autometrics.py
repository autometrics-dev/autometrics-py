from prometheus_client import Counter, Histogram, Gauge
import time
import inspect
import functools

prom_counter = Counter('function_calls_count', 'query??', ['function', 'module'])
prom_histogram = Histogram('function_calls_duration', 'query??', ['function', 'module'])
prom_guage = Gauge('function_calls_concurrent', 'query??', ['function', 'module'])

def function_calls_count(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = inspect.getmodule(func).__name__
        prom_counter.labels(func_name, module_name).inc()
        result = func(*args, **kwargs)
        return result
    return wrapper

def function_calls_duration(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = inspect.getmodule(func).__name__
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        prom_histogram.labels(func_name, module_name).observe(duration)
        return result
    return wrapper

def function_calls_concurrent(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = inspect.getmodule(func).__name__
        prom_guage.labels(func_name, module_name).set(time.time())
        result = func(*args, **kwargs)
        return result
    return wrapper

from prometheus_client import Counter, Histogram, Gauge
import time
import inspect
import functools

function_calls_counter = Counter('counter', 'query??', ['function', 'module'])
function_calls_histogram = Histogram('histogram', 'query??', ['function', 'module'])
function_calls_gauge = Gauge('gauge', 'query??', ['function', 'module'])

def function_calls_count(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = inspect.getmodule(func).__name__
        # start_time = time.time()
        function_calls_counter.labels(func_name, module_name).inc()
        result = func(*args, **kwargs)
        # duration = time.time() - start_time
        # prom_histogram.labels(func_name, module_name).observe(duration)
        return result
    return wrapper

def function_calls_duration(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = inspect.getmodule(func).__name__
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        function_calls_histogram.labels(func_name, module_name).observe(duration)
        return result
    return wrapper

def function_calls_concurrent(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = inspect.getmodule(func).__name__
        function_calls_gauge.labels(func_name, module_name).set(time.time())
        result = func(*args, **kwargs)
        return result
    return wrapper

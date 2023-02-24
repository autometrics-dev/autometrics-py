from prometheus_client import Counter, Histogram, Gauge
import time
import inspect
from prometheus_url import Generator
import os

prom_counter = Counter('function_calls_count', 'query??', ['function', 'module', 'result'])
prom_histogram = Histogram('function_calls_duration', 'query??', ['function', 'module'])
# prom_guage = Gauge('function_calls_concurrent', 'query??', ['function', 'module']) # we are not doing gauge atm

def autometrics(func):
    func_name = func.__name__
    fullname = func.__qualname__
    filename = get_filename_as_module(func)
    if fullname == func_name:
        module_name = filename
    else:
        classname = func.__qualname__.rsplit('.', 1)[0]
        module_name = f"{filename}.{classname}"
    def wrapper(*args, **kwargs):
        func_name = func.__name__
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
    g = Generator(func_name, module_name)
    urls = g.createURLs()
    wrapper.__doc__ = f'{func.__doc__}, Prometheus URLs {urls}'
    return wrapper

def get_filename_as_module(func):
    fullpath = inspect.getsourcefile(func)
    filename = os.path.basename(fullpath)
    module_part = os.path.splitext(filename)[0]
    return module_part
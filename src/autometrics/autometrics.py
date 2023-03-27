from prometheus_client import Counter, Histogram, Gauge
import time
import inspect
from .prometheus_url import Generator
import os
from functools import wraps

prom_counter = Counter('function_calls_count', 'query??', ['function', 'module', 'result', 'caller'])
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
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.time()
        caller = get_caller_function(func)
        try:
            result = func(*args, **kwargs)
            prom_counter.labels(func_name, module_name, 'ok', caller).inc()
        except Exception as e:
            result = e.__class__.__name__
            prom_counter.labels(func_name, module_name, 'error', caller).inc()
        duration = time.time() - start_time
        prom_histogram.labels(func_name, module_name).observe(duration)
        return result
    if func.__doc__ is not None:
        wrapper.__doc__ = f"{func.__doc__}\n{write_docs(func_name, module_name)}"
    else:
        wrapper.__doc__ = write_docs(func_name, module_name)
    return wrapper

def get_filename_as_module(func):
    fullpath = inspect.getsourcefile(func)
    filename = os.path.basename(fullpath)
    module_part = os.path.splitext(filename)[0]
    return module_part

def write_docs(func_name, module_name):
    g = Generator(func_name, module_name)
    urls = g.createURLs()
    docs = f"Prometheus Query URLs for Function - {func_name} and Module - {module_name}: \n\n"
    for key, value in urls.items():
        docs = f"{docs}{key} : {value} \n\n"
    docs = f"{docs}-------------------------------------------\n"
    return docs

def get_caller_function(func):
    caller_frame = inspect.stack()[2]
    caller_function_name = caller_frame[3]
    return caller_function_name
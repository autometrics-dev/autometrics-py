from prometheus_client import Counter, Histogram, Gauge
import time
import inspect
import builtins
import os

prom_counter = Counter('function_calls_count', 'query??', ['function', 'module', 'result'])
prom_histogram = Histogram('function_calls_duration', 'query??', ['function', 'module'])
# prom_guage = Gauge('function_calls_concurrent', 'query??', ['function', 'module']) # we are not doing gauge atm

def autometrics(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        filepart = get_filename_as_module(func)
        if args:
            class_name = args[0].__class__.__qualname__
            if class_name in check_if_builtin_type():
                module_name = filepart
            else:
                module_name = f"{filepart}.{class_name}"
        else:
            module_name = filepart
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

def check_if_builtin_type():
    builtin_type = []
    for name in dir(builtins):
        fullname = getattr(builtins, name)
        if isinstance(fullname, type):
            builtin_type.append(name)
    return builtin_type

def get_filename_as_module(func):
    fullpath = inspect.getsourcefile(func)
    filename = os.path.basename(fullpath)
    module_part = os.path.splitext(filename)[0]
    return module_part
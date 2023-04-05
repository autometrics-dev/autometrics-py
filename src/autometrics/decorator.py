"""Autometrics module."""
import inspect
import os
import time
from typing import Union
from collections.abc import Callable
from functools import wraps
from prometheus_client import Counter, Histogram
from .constants import (
    COUNTER_DESCRIPTION,
    HISTOGRAM_DESCRIPTION,
    OBJECTIVE_NAME_PROMETHEUS,
    OBJECTIVE_PERCENTILE_PROMETHEUS,
    OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
)
from .prometheus_url import Generator
from .objectives import Objective

prom_counter = Counter(
    "function_calls_count",
    COUNTER_DESCRIPTION,
    [
        "function",
        "module",
        "result",
        "caller",
        OBJECTIVE_NAME_PROMETHEUS,
        OBJECTIVE_PERCENTILE_PROMETHEUS,
    ],
)
prom_histogram = Histogram(
    "function_calls_duration",
    HISTOGRAM_DESCRIPTION,
    [
        "function",
        "module",
        OBJECTIVE_NAME_PROMETHEUS,
        OBJECTIVE_PERCENTILE_PROMETHEUS,
        OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS,
    ],
)


def autometrics(func: Callable, objective: Union[None, Objective] = None) -> Callable:
    """Decorator for tracking function calls and duration."""
    func_name = func.__name__
    fullname = func.__qualname__
    filename = get_filename_as_module(func)
    if fullname == func_name:
        module_name = filename
    else:
        classname = func.__qualname__.rsplit(".", 1)[0]
        module_name = f"{filename}.{classname}"

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.time()
        caller = get_caller_function()

        try:
            result = func(*args, **kwargs)
            prom_counter.labels(
                func_name,
                module_name,
                "ok",
                caller,
                "" if objective is None else objective.name,
                ""
                if objective is None or objective.success_rate is None
                else objective.success_rate,
            ).inc()
        except Exception as exception:
            result = exception.__class__.__name__
            prom_counter.labels(
                func_name,
                module_name,
                "error",
                caller,
                "" if objective is None else objective.name,
                ""
                if objective is None or objective.success_rate is None
                else objective.success_rate,
            ).inc()

        duration = time.time() - start_time
        prom_histogram.labels(
            func_name,
            module_name,
            "" if objective is None else objective.name,
            ""
            if objective is None or objective.latency is None
            else objective.latency[1],
            ""
            if objective is None or objective.latency is None
            else objective.latency[0],
        ).observe(duration)
        return result

    if func.__doc__ is not None:
        wrapper.__doc__ = f"{func.__doc__}\n{write_docs(func_name, module_name)}"
    else:
        wrapper.__doc__ = write_docs(func_name, module_name)
    return wrapper


def get_filename_as_module(func: Callable) -> str:
    """Get the filename of the module that contains the function."""
    fullpath = inspect.getsourcefile(func)
    if fullpath == None:
        return ""

    filename = os.path.basename(fullpath)
    module_part = os.path.splitext(filename)[0]
    return module_part


def write_docs(func_name: str, module_name: str):
    """Write the prometheus query urls to the function docstring."""
    g = Generator(func_name, module_name)
    docs = f"Prometheus Query URLs for Function - {func_name} and Module - {module_name}: \n\n"

    urls = g.createURLs()
    for key, value in urls.items():
        docs = f"{docs}{key} : {value} \n\n"

    docs = f"{docs}-------------------------------------------\n"
    return docs


def get_caller_function():
    """Get the name of the function that called the function being decorated."""
    caller_frame = inspect.stack()[2]
    caller_function_name = caller_frame[3]
    return caller_function_name

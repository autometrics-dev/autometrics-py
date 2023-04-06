"""Autometrics module."""
import inspect
import os
import time
from typing import Union
from collections.abc import Callable
from functools import wraps
from .prometheus_url import Generator
from .objectives import Objective
from .emit import count, histogram


def autometrics(func: Callable, objective: Union[None, Objective] = None) -> Callable:
    """Decorator for tracking function calls and duration."""
    module_name = get_module_name(func)
    func_name = func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        caller = get_caller_function()

        try:
            result = func(*args, **kwargs)
            count(func_name, module_name, caller, objective, "ok")
        except Exception as exception:
            result = exception.__class__.__name__
            count(func_name, module_name, caller, objective, "error")

        histogram(func_name, module_name, start_time, objective)
        return result

    if func.__doc__ is None:
        wrapper.__doc__ = write_docs(func_name, module_name)
    else:
        wrapper.__doc__ = f"{func.__doc__}\n{write_docs(func_name, module_name)}"
    return wrapper


def get_module_name(func: Callable) -> str:
    """Get the name of the module that contains the function."""
    func_name = func.__name__
    fullname = func.__qualname__
    filename = get_filename_as_module(func)
    if fullname == func_name:
        return filename

    classname = func.__qualname__.rsplit(".", 1)[0]
    return f"{filename}.{classname}"


def get_filename_as_module(func: Callable) -> str:
    """Get the filename of the module that contains the function."""
    fullpath = inspect.getsourcefile(func)
    if fullpath is None:
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

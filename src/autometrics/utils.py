import inspect
import os

from collections.abc import Callable
from prometheus_client import start_wsgi_server, REGISTRY, CollectorRegistry

from .prometheus_url import Generator


def get_module_name(func: Callable) -> str:
    """Get the name of the module that contains the function."""
    module = inspect.getmodule(func)
    if module is None:
        return get_filename_as_module(func)
    return module.__name__


def get_filename_as_module(func: Callable) -> str:
    """Get the filename of the module that contains the function."""
    fullpath = inspect.getsourcefile(func)
    if fullpath is None:
        return ""

    filename = os.path.basename(fullpath)
    module_part = os.path.splitext(filename)[0]
    return module_part


def get_function_name(func: Callable) -> str:
    """Get the name of the function."""
    return func.__qualname__ or func.__name__


def write_docs(func_name: str, module_name: str):
    """Write the prometheus query urls to the function docstring."""
    generator = Generator(func_name, module_name)
    docs = f"Prometheus Query URLs for Function - {func_name} and Module - {module_name}: \n\n"

    urls = generator.create_urls()
    for key, value in urls.items():
        docs = f"{docs}{key} : {value} \n\n"

    docs = f"{docs}-------------------------------------------\n"
    return docs


def append_docs_to_docstring(func, func_name, module_name):
    """Helper for appending docs to a function's docstring."""
    if func.__doc__ is None:
        return write_docs(func_name, module_name)
    else:
        return f"{func.__doc__}\n{write_docs(func_name, module_name)}"


def start_http_server(
    port: int = 9464, addr: str = "0.0.0.0", registry: CollectorRegistry = REGISTRY
):
    """Starts a WSGI server for prometheus metrics as a daemon thread."""
    start_wsgi_server(port, addr, registry)

import inspect
import os
from collections.abc import Callable
from .prometheus_url import Generator


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


def get_caller_function(depth: int = 2):
    """Get the name of the function. Default depth is 2 to get the caller of the caller of the function being decorated."""
    caller_frame = inspect.stack()[depth]
    caller_function_name = caller_frame[3]
    return caller_function_name

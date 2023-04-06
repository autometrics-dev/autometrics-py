"""Autometrics module."""
import time
from typing import Union, overload, TypeVar, Any, Callable, Optional
from typing_extensions import ParamSpec
from functools import wraps
from .objectives import Objective
from .emit import count, histogram, Result
from .utils import get_module_name, get_caller_function, write_docs


P = ParamSpec("P")
T = TypeVar("T")


# Bare decorator usage
@overload
def autometrics(func: Callable[P, T]) -> Callable[P, T]:
    ...


# Decorator with arguments
@overload
def autometrics(*, objective: Optional[Objective] = None) -> Callable:
    ...

def autometrics(
    func: Optional[Callable] = None,
    *,
    objective: Optional[Objective] = None,
):
    """Decorator for tracking function calls and duration."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        module_name = get_module_name(func)
        func_name = func.__name__

        @wraps(func)
        def wrapper(*args: P.args, **kwds: P.kwargs) -> T:
            start_time = time.time()
            caller = get_caller_function()

            try:
                result = func(*args, **kwds)
                count(func_name, module_name, caller, objective, result=Result.OK)
                histogram(func_name, module_name, start_time, objective)
            except Exception as exception:
                result = exception.__class__.__name__
                count(func_name, module_name, caller, objective, result=Result.ERROR)
                histogram(func_name, module_name, start_time, objective)
                # Reraise exception
                raise exception
            return result

        if func.__doc__ is None:
            wrapper.__doc__ = write_docs(func_name, module_name)
        else:
            wrapper.__doc__ = f"{func.__doc__}\n{write_docs(func_name, module_name)}"
        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)

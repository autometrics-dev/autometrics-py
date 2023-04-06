"""Autometrics module."""
import time
from typing import Union, overload, TypeVar, Any, Callable, Optional
from functools import wraps
from .objectives import Objective
from .emit import count, histogram
from .utils import get_module_name, get_caller_function, write_docs


F = TypeVar("F", bound=Callable[..., Any])


# Bare decorator usage
@overload
def autometrics(func: F) -> F:
    ...


# Decorator with arguments
@overload
def autometrics(*, objective: Union[None, Objective] = None) -> Callable[[F], F]:
    ...


def autometrics(
    func: Optional[Callable[..., Any]] = None,
    *,
    objective: Union[None, Objective] = None,
):
    """Decorator for tracking function calls and duration."""

    def decorator(func: F) -> F:
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

    if func is None:
        return decorator
    else:
        return decorator(func)

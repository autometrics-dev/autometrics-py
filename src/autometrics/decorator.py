"""Autometrics module."""
import time
import inspect

# import asyncio
from functools import wraps
from typing import overload, TypeVar, Callable, Optional, Coroutine, Any
from typing_extensions import ParamSpec
from .objectives import Objective
from .tracker import get_tracker, Result
from .utils import get_module_name, get_caller_function, append_docs_to_docstring


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
    def track_result_ok(start_time: float, function: str, module: str, caller: str):
        get_tracker().finish(
            start_time,
            function=function,
            module=module,
            caller=caller,
            objective=objective,
            result=Result.OK,
        )

    def track_result_error(
        exception: Exception,
        start_time: float,
        function: str,
        module: str,
        caller: str,
    ):
        get_tracker().finish(
            start_time,
            function=function,
            module=module,
            caller=caller,
            objective=objective,
            result=Result.ERROR,
        )
        # Reraise exception
        raise exception

    """Decorator for tracking function calls and duration."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        module_name = get_module_name(func)
        func_name = func.__name__

        def sync_wrapper_helper(
            func: Callable[P, T], *args: P.args, **kwds: P.kwargs
        ) -> T:
            start_time = time.time()
            caller = get_caller_function()

            try:
                result = func(*args, **kwds)
                track_result_ok(
                    start_time, function=func_name, module=module_name, caller=caller
                )

            except Exception as exception:
                result = exception.__class__.__name__
                track_result_error(
                    exception,
                    start_time,
                    function=func_name,
                    module=module_name,
                    caller=caller,
                )
                # Reraise exception
                raise exception
            return result

        async def async_wrapper_helper(
            func: Callable[P, T], *args: P.args, **kwds: P.kwargs
        ) -> T:
            start_time = time.time()
            caller = get_caller_function()

            try:
                result = await func(*args, **kwds)
                track_result_ok(
                    start_time, function=func_name, module=module_name, caller=caller
                )

            except Exception as exception:
                result = exception.__class__.__name__
                track_result_error(
                    exception,
                    start_time,
                    function=func_name,
                    module=module_name,
                    caller=caller,
                )
                # Reraise exception
                raise exception
            return result

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: P.args, **kwds: P.kwargs) -> T:
                return await async_wrapper_helper(func, *args, **kwds)

            async_wrapper.__doc__ = append_docs_to_docstring(
                func, func_name, module_name
            )
            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args: P.args, **kwds: P.kwargs) -> T:
                return sync_wrapper_helper(func, *args, **kwds)

            sync_wrapper.__doc__ = append_docs_to_docstring(
                func, func_name, module_name
            )
            return sync_wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)

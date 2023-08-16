"""Autometrics module."""
import time
import inspect

from contextvars import ContextVar, Token
from functools import wraps
from typing import overload, TypeVar, Callable, Optional, Awaitable
from typing_extensions import ParamSpec

from .objectives import Objective
from .tracker import get_tracker, Result
from .utils import (
    get_function_name,
    get_module_name,
    append_docs_to_docstring,
)


P = ParamSpec("P")
T = TypeVar("T")


caller_module_var: ContextVar[str] = ContextVar("caller.module", default="")
caller_function_var: ContextVar[str] = ContextVar("caller.function", default="")


# Bare decorator usage
@overload
def autometrics(func: Callable[P, T]) -> Callable[P, T]:
    ...


@overload
def autometrics(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    ...


# Decorator with arguments
@overload
def autometrics(
    *, objective: Optional[Objective] = None, track_concurrency: Optional[bool] = False
) -> Callable:
    ...


def autometrics(
    func: Optional[Callable] = None,
    *,
    objective: Optional[Objective] = None,
    track_concurrency: Optional[bool] = False,
):
    """Decorator for tracking function calls and duration. Supports synchronous and async functions."""

    def register_function_info(
        function: str,
        module: str,
    ):
        get_tracker().initialize_counters(
            function=function, module=module, objective=objective
        )

    def track_start(function: str, module: str):
        get_tracker().start(
            function=function, module=module, track_concurrency=track_concurrency
        )

    def track_result_ok(
        start_time: float,
        function: str,
        module: str,
        caller_module: str,
        caller_function: str,
    ):
        get_tracker().finish(
            start_time,
            function=function,
            module=module,
            caller_module=caller_module,
            caller_function=caller_function,
            objective=objective,
            track_concurrency=track_concurrency,
            result=Result.OK,
        )

    def track_result_error(
        start_time: float,
        function: str,
        module: str,
        caller_module: str,
        caller_function: str,
    ):
        get_tracker().finish(
            start_time,
            function=function,
            module=module,
            caller_module=caller_module,
            caller_function=caller_function,
            objective=objective,
            track_concurrency=track_concurrency,
            result=Result.ERROR,
        )

    def sync_decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Helper for decorating synchronous functions, to track calls and duration."""

        module_name = get_module_name(func)
        func_name = get_function_name(func)
        register_function_info(func_name, module_name)

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwds: P.kwargs) -> T:
            start_time = time.time()
            caller_module = caller_module_var.get()
            caller_function = caller_function_var.get()
            context_token_module: Optional[Token] = None
            context_token_function: Optional[Token] = None

            try:
                context_token_module = caller_module_var.set(module_name)
                context_token_function = caller_function_var.set(func_name)
                if track_concurrency:
                    track_start(module=module_name, function=func_name)
                result = func(*args, **kwds)
                track_result_ok(
                    start_time,
                    function=func_name,
                    module=module_name,
                    caller_module=caller_module,
                    caller_function=caller_function,
                )

            except Exception as exception:
                result = exception.__class__.__name__
                track_result_error(
                    start_time,
                    function=func_name,
                    module=module_name,
                    caller_module=caller_module,
                    caller_function=caller_function,
                )
                # Reraise exception
                raise exception

            finally:
                if context_token_module is not None:
                    caller_module_var.reset(context_token_module)
                if context_token_function is not None:
                    caller_function_var.reset(context_token_function)

            return result

        sync_wrapper.__doc__ = append_docs_to_docstring(func, func_name, module_name)
        return sync_wrapper

    def async_decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        """Helper for decorating async functions, to track calls and duration."""

        module_name = get_module_name(func)
        func_name = get_function_name(func)
        register_function_info(func_name, module_name)

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwds: P.kwargs) -> T:
            start_time = time.time()
            caller_module = caller_module_var.get()
            caller_function = caller_function_var.get()
            context_token_module: Optional[Token] = None
            context_token_function: Optional[Token] = None

            try:
                context_token_module = caller_module_var.set(module_name)
                context_token_function = caller_function_var.set(func_name)
                if track_concurrency:
                    track_start(module=module_name, function=func_name)
                result = await func(*args, **kwds)
                track_result_ok(
                    start_time,
                    function=func_name,
                    module=module_name,
                    caller_module=caller_module,
                    caller_function=caller_function,
                )

            except Exception as exception:
                result = exception.__class__.__name__
                track_result_error(
                    start_time,
                    function=func_name,
                    module=module_name,
                    caller_module=caller_module,
                    caller_function=caller_function,
                )
                # Reraise exception
                raise exception

            finally:
                if context_token_module is not None:
                    caller_module_var.reset(context_token_module)
                if context_token_function is not None:
                    caller_function_var.reset(context_token_function)

            return result

        async_wrapper.__doc__ = append_docs_to_docstring(func, func_name, module_name)
        return async_wrapper

    def pick_decorator(func: Callable) -> Callable:
        """Pick the correct decorator based on the function type."""
        if inspect.iscoroutinefunction(func):
            return async_decorator(func)
        return sync_decorator(func)

    if func is None:
        return pick_decorator
    elif inspect.iscoroutinefunction(func):
        return async_decorator(func)
    else:
        return sync_decorator(func)

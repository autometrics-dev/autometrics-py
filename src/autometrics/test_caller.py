"""Tests for caller tracking."""
from functools import wraps
from prometheus_client.exposition import generate_latest

from .decorator import autometrics
from .initialization import init


def test_caller_detection():
    """This is a test to see if the caller is properly detected."""
    init()

    def dummy_decorator(func):
        @wraps(func)
        def dummy_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return dummy_wrapper

    def another_decorator(func):
        @wraps(func)
        def another_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return another_wrapper

    @dummy_decorator
    @autometrics
    @another_decorator
    def foo():
        pass

    @autometrics
    def bar():
        foo()

    bar()

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")

    expected = """function_calls_total{caller_function="test_caller_detection.<locals>.bar",caller_module="autometrics.test_caller",function="test_caller_detection.<locals>.foo",module="autometrics.test_caller",objective_name="",objective_percentile="",result="ok",service_name="autometrics"} 1.0"""
    assert "wrapper" not in data
    assert expected in data
